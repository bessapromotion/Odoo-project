# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.tools import conversion


class OrdrePaiement(models.Model):
    _name = 'ordre.paiement'
    _description = 'Ordre de paiement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('amount')
    def _display_number_to_word(self):
        for rec in self:
            rec.amount_lettre = conversion.conversion(rec.amount)

    name                 = fields.Char(u'Numéro', required=True, readonly="1", default='/')
    date                 = fields.Date('Date du paiement', required=True, default=date.today(), readonly=1, states={'open': [('readonly', False)]})
    order_id             = fields.Many2one('sale.order', string='Commande', required=True, readonly=True)
    echeance_id          = fields.Many2one('crm.echeancier', string='Echeance', readonly=True)
    partner_id           = fields.Many2one(related='order_id.partner_id', string='Client', readonly=True, required=True)
    commercial_id        = fields.Many2one('res.users', string='Commercial', required=True, readonly=True, states={'open': [('readonly', False)]})
    partner_reference    = fields.Char(u'Référence client', readonly=1, states={'open': [('readonly', False)]})
    project_id           = fields.Many2one(related='order_id.project_id', string='Projet', readonly=True, required=True)
    currency_id          = fields.Many2one(related='order_id.currency_id', readonly=True)
    amount               = fields.Monetary('Montant', required=True, readonly=1, states={'open': [('readonly', False)]})
    amount_lettre        = fields.Char(compute=_display_number_to_word, string='Montant en lettres', readonly=1)
    mode_paiement_id     = fields.Many2one('mode.paiement', string='Mode de paiement', required=True, readonly=1, states={'open': [('readonly', False)]})
    objet                = fields.Char('Motif de paiement', readonly=1, states={'open': [('readonly', False)]})
    doc_payment_id       = fields.Many2one('payment.doc', string=u'Numéro', readonly=1, states={'open': [('readonly', False)]})
    cheque_domiciliation = fields.Char(related='doc_payment_id.domiciliation', string='Domiciliation', readonly=1)
    cheque_ordonateur    = fields.Char(related='doc_payment_id.ordonateur', string='Ordonateur', readonly=1)
    cheque_date          = fields.Date(related='doc_payment_id.date', string=u'Date', readonly=1)
    cheque_objet         = fields.Selection(related='doc_payment_id.objet', string='Objet de Chèque', readonly=1)
    cheque_type          = fields.Selection(related='doc_payment_id.type', string='Type de Chèque', readonly=1)
    observation          = fields.Char('Observation')
    state                = fields.Selection([('open', 'En instance de paiement'), ('done', u'Terminé'), ('cancel', u'Annulé')])

    @api.onchange('partner_id')
    def onchange_partner(self):
        self.cheque_ordonateur = self.partner_id.name

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('ordre.paiement') or '/'

        return super(OrdrePaiement, self).create(vals)

    @api.multi
    def action_print_recu_paiement(self):
        req1 = "delete from echeance_amount_wizard"
        req2 = "delete from creer_paiement_wizard"
        self._cr.execute(req1, )
        self._cr.execute(req2, )
        data_obj = self.env['ir.model.data']

        form_data_id = data_obj._get_id('crm_echeancier', 'creer_paiement_wizard_form_view')
        form_view_id = False
        if form_data_id:
            form_view_id = data_obj.browse(form_data_id).res_id

        return {
            'name': 'Assistant impression recu de paiement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(form_view_id, 'form'), ],
            'res_model': 'creer.paiement.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_name': self.id,
                        'default_amount': self.amount,
                        'default_payment_date': self.date,
                        'default_communication': self.objet,
                        'default_doc_payment_id': self.doc_payment_id.id,
                        'default_mode_paiement_id': self.mode_paiement_id.id,
                        'default_partner_reference': self.partner_reference,
                        'default_observation': self.observation,
                        },
            'target': 'new',
        }
