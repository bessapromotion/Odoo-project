# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.tools import conversion
from odoo.exceptions import UserError


class OrdrePaiement(models.Model):
    _name = 'ordre.paiement'
    _description = 'Ordre de paiement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('amount')
    def _display_number_to_word(self):
        for rec in self:
            rec.amount_lettre = conversion.conversion(rec.amount)

    name = fields.Char(u'Numéro', required=True, readonly="1", default='/')
    date = fields.Date('Date du paiement', required=True, default=date.today(), readonly=1,
                       states={'open': [('readonly', False)]})
    order_id = fields.Many2one('sale.order', string='Commande', required=True, readonly=True)
    echeance_id = fields.Many2one('crm.echeancier', string='Echeance', readonly=True)
    partner_id = fields.Many2one(related='order_id.partner_id', string='Client', readonly=True, required=True)
    commercial_id = fields.Many2one('res.users', string='Commercial', required=True, readonly=True,
                                    states={'open': [('readonly', False)]})
    partner_reference = fields.Char(u'Référence client', readonly=1, states={'open': [('readonly', False)]})
    project_id = fields.Many2one(related='order_id.project_id', string='Projet', readonly=True, required=True, store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', readonly=True)
    amount = fields.Monetary('Montant', required=True, readonly=1, states={'open': [('readonly', False)]})
    amount_lettre = fields.Char(compute=_display_number_to_word, string='Montant en lettres', readonly=1)
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement', required=True, readonly=1,
                                       states={'open': [('readonly', False)]})
    objet = fields.Char('Motif de paiement', readonly=1, states={'open': [('readonly', False)]})
    doc_payment_id = fields.Many2one('payment.doc', string=u'Numéro', readonly=1,
                                     states={'open': [('readonly', False)]})
    cheque_domiciliation = fields.Char(related='doc_payment_id.domiciliation', string='Domiciliation', readonly=1)
    cheque_ordonateur = fields.Char(related='doc_payment_id.ordonateur', string='Ordonateur', readonly=1)
    cheque_date = fields.Date(related='doc_payment_id.date', string=u'Date', readonly=1)
    cheque_objet = fields.Selection(related='doc_payment_id.objet', string='Objet de Chèque', readonly=1)
    cheque_type = fields.Selection(related='doc_payment_id.type', string='Type de Chèque', readonly=1)
    observation = fields.Char('Observation')
    state = fields.Selection([('open', 'En instance de paiement'), ('done', u'Terminé'), ('cancel', u'Annulé')])
    company_id = fields.Many2one('res.company', u'Société', related='order_id.project_id.company_id', store=True)

    # annulation
    motif_annulation_id = fields.Many2one('annuler.paiement.motif', string='Motif d\'annulation', readonly=True, )
    annuler_user_id = fields.Many2one('res.users', string='Annulé par', readonly=True, )
    date_annulation = fields.Datetime(string='Date', readonly=True, )
    payment_id = fields.Many2one('account.payment', readonly=True, string='Paiement')

    @api.onchange('partner_id')
    def onchange_partner(self):
        self.cheque_ordonateur = self.partner_id.name

    def action_cancel(self):
        if self.state == 'done':
            if not self.payment_id:
                payment_id = self.env['account.payment'].search([('echeance_id', '=', self.echeance_id.id),
                                                                 ('date', '=', self.date),
                                                                 ('amount', '=', self.amount),
                                                                 ('state', '=', 'posted'), ])

                if payment_id.exists():
                    self.payment_id = payment_id[0].id

        view_id = self.env['ir.model.data']._xmlid_to_res_id('crm_echeancier.annuler_paiement_wizard_form_view')
        return {
            'name': 'Assistant annulation ordre de paiement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(view_id, 'form'), ],
            'res_model': 'annuler.paiement.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_name': self.id,
                        'default_payment_id': self.payment_id.id,
                        },
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('ordre.paiement') or '/'

        return super(OrdrePaiement, self).create(vals)

    def action_print_recu_paiement(self):
        if self.company_id.id != self.env.company.id:
            raise UserError(_(u'Veuillez sélectionner la société %s', self.company_id.name))
        req1 = "delete from echeance_amount_wizard"
        req2 = "delete from creer_paiement_wizard"
        self._cr.execute(req1, )
        self._cr.execute(req2, )

        view_id = self.env['ir.model.data']._xmlid_to_res_id('crm_echeancier.creer_paiement_wizard_form_view')

        return {
            'name': 'Assistant impression recu de paiement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(view_id, 'form'), ],
            'res_model': 'creer.paiement.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_name': self.id,
                        'default_amount': self.amount,
                        'default_amount_commercial': self.amount,
                        'default_payment_date': self.date,
                        'default_communication': self.objet,
                        'default_doc_payment_id': self.doc_payment_id.id,
                        'default_mode_paiement_id': self.mode_paiement_id.id,
                        'default_partner_reference': self.partner_reference,
                        'default_observation': self.observation,
                        },
            'target': 'new',
        }
