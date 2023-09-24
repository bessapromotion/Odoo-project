# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date


class CrmEcheancier(models.Model):
    _name = 'crm.echeancier'
    _description = 'Echeance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.one
    @api.depends('payment_ids', 'montant_prevu')
    def _total_paiement(self):
        total = 0.0
        for rec in self:
            if rec.type != 'remboursement':
                for line in rec.payment_ids:
                    total += line.amount
                rec.montant = total
                rec.montant_restant = rec.montant_prevu - total
            else:
                rec.montant = 0
                rec.montant_restant = 0

    name          = fields.Char(u'Numéro', readonly=1)
    order_id      = fields.Many2one('sale.order', string='Commande', readonly=1, states={'draft': [('readonly', False)]})
    order_id_state      = fields.Selection(related='order_id.state', string='Etat Bon de commande', readonly=1, store=True)
    label         = fields.Char('Designation')

    currency_id = fields.Many2one(related='order_id.currency_id')
    amount_total_signed = fields.Monetary(related='order_id.amount_total', string='Total a payer', currency_field='currency_id', readonly=True)
    # residual_signed   = fields.Monetary(related='invoice_id.residual_signed', string='Reste a payer', currency_field='currency_id', readonly=True)

    partner_id    = fields.Many2one(related='order_id.partner_id', string='Client', readonly=1, store=True)
    phone         = fields.Char(related='order_id.partner_id.phone', string='Téléphone', readonly=1)
    mobile        = fields.Char(related='order_id.partner_id.mobile', string='Mobile', readonly=1)
    project_id     = fields.Many2one(related='order_id.project_id', string='Projet', readonly=1, store=True)
    commercial_id = fields.Many2one(related='order_id.user_id', string='Commercial', readonly=1, store=True)
    charge_recouv_id = fields.Many2one(related='order_id.charge_recouv_id', readonly=1, store=True, string=u'Recouvrement')

    date_creation = fields.Date('Date', required=1, readonly=1, states={'draft': [('readonly', False)]}, default=date.today())
    date_prevue   = fields.Date('Date de paiement prévue', required=1, track_visibility='onchange', readonly=1, states={'draft': [('readonly', False)]})
    date_paiement = fields.Date('Date de paiement', track_visibility='onchange', readonly=1, states={'draft': [('readonly', False)]})

    # taux          = fields.Float('Taux', track_visibility='onchange', readonly=1, states={'draft': [('readonly', False)]})
    montant_prevu = fields.Monetary('Montant prevu', track_visibility='onchange', readonly=1)  # , states={'draft': [('readonly', False)]})
    montant       = fields.Monetary(compute=_total_paiement, string=u'Montant payé', track_visibility='onchange', readonly=1, store=True)
    montant_restant = fields.Monetary(compute=_total_paiement, string=u'Reste à payer', store=True, readonly=1, track_visibility='onchange')
    observation   = fields.Text('Observation')
    state         = fields.Selection([('draft', 'Nouveau'),
                                      ('open', 'Ouvert'),
                                      ('inprogress', 'En instance de paiement'),
                                      ('done', 'Payé'),
                                      ('cancel', 'Annulé'),
                                      ], string='Etat', default='open', track_visibility='onchange')
    type          = fields.Selection([('tranche', 'Tranche'), ('tva', 'TVA'), ('notaire', 'Notaire'), ('remboursement', 'Ajustement Remboursement')], string='Type', default='tranche', readonly=True)
    payment_ids   = fields.One2many('account.payment', 'echeance_id', string='Paiements')

    # @api.onchange('montant_prevu')
    # def onchange_montant_prevu(self):
    #     if self.montant_prevu:
    #         if self.amount_total_signed != 0:
    #             self.taux  = self.montant_prevu / self.amount_total_signed * 100
    #         else:
    #             self.taux = 0.0

    # @api.model
    # def create(self, vals):
    #     req = "select max(name) as num from crm_reservation where date_part('year', date)=%s;"
    #     self._cr.execute(req, (datetime.now().year,))
    #     res = self._cr.dictfetchall()
    #     num = res[0].get('num')
    #     if not num:
    #         num = str(datetime.now())[2:4] + '/0000001'
    #     else:
    #         tmp = num[7:]
    #         vtmp = int(tmp) + 1
    #         num = str(datetime.now())[2:4] + '/' + "{0:0>7}".format(str(vtmp))
    #
    #     vals['name'] = num
    #
    #     return super(CrmReservation, self).create(vals)

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Suppression non autorisée ! \n\n  L\'echeance est déjà validée !'))
        else:
            rec = super(CrmEcheancier, self).unlink()
            return rec

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_send_to_payment(self):
        # self.state = 'inprogress'
        data_obj = self.env['ir.model.data']

        form_data_id = data_obj._get_id('crm_echeancier', 'print_ordre_paiement_wizard_form_view')
        form_view_id = False
        if form_data_id:
            form_view_id = data_obj.browse(form_data_id).res_id

        return {
            'name': 'Assistant impression Ordre de paiement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(form_view_id, 'form'), ],
            'res_model': 'print.ordre.paiement.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_echeance_id': self.id,
                        'default_order_id': self.order_id.id,
                        'default_commercial_id': self.commercial_id.id,
                        'default_objet': self.label,
                        'default_amount': self.montant_restant},
            'target': 'new',
        }

    @api.one
    def action_validate(self):
        self.state = 'open'

    @api.one
    def action_draft(self):
        self.state = 'draft'

    @api.one
    def action_paiement(self):
        self.state = 'done'
        self.date_paiement = date.today()
        self.montant = self.montant_prevu

    @api.multi
    def wizard_change_amount(self):
        # Reste à payer global
        lst = self.env['crm.echeancier'].search([('order_id', '=', self.order_id.id), ('state', 'in', ('draft', 'open'))])
        mtn_total = sum(line.montant_restant for line in lst)

        data_obj = self.env['ir.model.data']

        form_data_id = data_obj._get_id('crm_echeancier', 'echeance_amount_wizard_form_view')
        form_view_id = False
        if form_data_id:
            form_view_id = data_obj.browse(form_data_id).res_id

        return {
                'name'     : 'Changement du montant prevu',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id'  : False,
                'views'    : [(form_view_id, 'form'), ],
                'res_model': 'echeance.amount.wizard',
                'type'     : 'ir.actions.act_window',
                'context'  : {'default_name': self.id,
                              'default_amount': self.montant_restant,
                              'default_reste_global': mtn_total,
                              },
                'target'   : 'new',
        }
