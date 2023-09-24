# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class CrmRemboursement(models.Model):
    _name = 'crm.remboursement'
    _description = 'Remboursement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    @api.depends('montant_a_rembourser', 'payment_ids')
    def _montants(self):
        for rec in self:
            rec.montant_rembourse = sum(line.amount for line in rec.payment_ids)
            rec.montant_restant = rec.montant_a_rembourser - rec.montant_rembourse

    name           = fields.Char(u'Numéro', readonly=1)
    commercial_id = fields.Many2one('res.users', required=1, string='Commercial', readonly=1, states={'open': [('readonly', False)]})
    charge_rembours_id = fields.Many2one('res.users', required=1, string=u'Chargé remboursement')  # , readonly=1, states={'desistement': [('readonly', False)]})
    date      = fields.Date('Date', readonly=True)
    motif     = fields.Text('Motif', readonly=True)
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement')
    state     = fields.Selection([('open', u'En cours'),
                                  ('done', u'Clôturé'),
                                  ('cancel', u'Annulée'), ], string='Etat', default='open', tracking=True)

    annulation_id = fields.Many2one('crm.annulation', string='Demande Annulation', readonly=True)
    reservation_id = fields.Many2one('crm.reservation', string=u'Réservation', readonly=True)
    echeancier_ids = fields.One2many(related='reservation_id.echeancier_ids', readonly=True, string='Echeances', domain="[('state', '=', 'done')]")
    montant_a_rembourser = fields.Monetary(u'Montant à rembourser', readonly=1)
    montant_rembourse    = fields.Monetary(compute=_montants, string=u'Montant remboursé', readonly=1)
    montant_restant      = fields.Monetary(compute=_montants, string=u'Reste à rembourser', readonly=1)
    currency_id = fields.Many2one(related='reservation_id.currency_id', string='Devise')

    partner_id    = fields.Many2one(related='reservation_id.partner_id', string='Client', readonly=1, store=True)
    phone         = fields.Char(related='partner_id.phone', string='Téléphone', readonly=1)
    mobile        = fields.Char(related='partner_id.mobile', string='Mobile', readonly=1)
    photo         = fields.Binary(related='partner_id.image_1920', string='Photo')
    payment_ids   = fields.One2many('account.payment', 'remboursement_id', string='Paiements')
    company_id = fields.Many2one('res.company', u'Société', related='reservation_id.project_id.company_id', store=True)

    @api.model
    def create(self, vals):
        # req = "select max(name) as num from crm_remboursement where date_part('year', date)=%s;"
        # self._cr.execute(req, (datetime.now().year,))
        # res = self._cr.dictfetchall()
        # num = res[0].get('num')
        # if not num:
        #     num = 'REM/' + str(datetime.now())[2:4] + '/0000001'
        # else:
        #     tmp = num[7:]
        #     vtmp = int(tmp) + 1
        #     num = 'REM/' + str(datetime.now())[2:4] + '/' + "{0:0>7}".format(str(vtmp))

        vals['name'] = self.env['ir.sequence'].get('crm.remboursement') or '/'

        return super(CrmRemboursement, self).create(vals)

    # @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Suppression non autorisée ! \n\n  Le remboursement est déjà validée !'))
        else:

            rec = super(CrmRemboursement, self).unlink()
            return rec

    # @api.one
    def action_cancel(self):
        self.state = 'cancel'

    # @api.multi
    def action_create_payment(self):
        # data_obj = self.env['ir.model.data']
        #
        # form_data_id = data_obj._get_id('crm_remboursement', 'creer_paiement_out_wizard_form_view')
        # form_view_id = False
        # if form_data_id:
        #     form_view_id = data_obj.browse(form_data_id).res_id

        view_id = self.env['ir.model.data']._xmlid_to_res_id('crm_remboursement.creer_paiement_out_wizard_form_view')

        return {
            'name': 'Créer un nouveau remboursement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(view_id, 'form'), ],
            'res_model': 'creer.paiement.out.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_name': self.id,
                        'default_amount': self.montant_restant,
                        'default_payment_date': self.date,
                        'default_communication': 'Remboursement'
                        },
            'target': 'new',
                }
