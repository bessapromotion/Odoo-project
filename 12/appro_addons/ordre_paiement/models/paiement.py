# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import conversion
from datetime import date


class OrdrePaiement(models.Model):
    _name    = 'ordre.paiement'
    _description    = 'Ordre de paiement'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('amount')
    def _display_number_to_word(self):
        self.amount_lettre = conversion.conversion(self.amount)

    name = fields.Char('Numero', readonly=1, default='/')
    type = fields.Selection([('invoice', 'Sur facture'), ('order', u'Anticipé')], string='Type', default='invoice')
    order_id = fields.Many2one('purchase.order', string='Bon de commande')
    invoice_id = fields.Many2one('account.invoice', string='Facture')
    requisition_id = fields.Many2one(related='order_id.requisition_id', string='Consultation', readonly=1)
    partner_id = fields.Many2one('res.partner', string='Fournisseur')
    user_id = fields.Many2one('res.users', string='Responsable')
    amount = fields.Monetary('Montant')
    currency_id = fields.Many2one(related='order_id.currency_id', string='Devise', readonly=1)

    amount_lettre = fields.Char(compute=_display_number_to_word, string='Montant en lettres', readonly=1)
    mode_paiement_id = fields.Many2one('payment.mode', string='Mode de paiement')

    objet = fields.Char(u'Objet du réglement')
    date = fields.Date(u'Date établissement', default=date.today())
    date_ordonnancement = fields.Date('Bon pour ordonnacement le ')
    date_paiement = fields.Date('Bon pour paiement le ')
    observation = fields.Text('Observation')
    state = fields.Selection([('draft', 'Nouveau'),
                              ('traitement', 'En traitement'),
                              ('ordonnancement', 'Ordonnancement'),
                              ('open', 'En instance de paiement'),
                              ('done', u'Terminé'),
                              ('cancel', u'Annulé')], string='Etat', default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('ordre.paiement') or '/'

        return super(OrdrePaiement, self).create(vals)

    @api.onchange('order_id')
    def onchange_commande(self):
        self.amount = self.order_id.amount_total
        self.objet = self.order_id.requisition_id.objet

    @api.onchange('invoice_id')
    def onchange_invoice(self):
        self.amount = self.invoice_id.amount_total

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_send_to_traitment(self):
        self.state = 'traitement'

    @api.one
    def action_bon_ordonnacement(self):
        self.state = 'ordonnancement'
        self.date_ordonnancement = date.today()

    @api.one
    def action_bon_paiement(self):
        self.state = 'open'
        self.date_paiement = date.today()

    @api.multi
    def action_print_recu_paiement(self):
        data_obj = self.env['ir.model.data']

        form_data_id = data_obj._get_id('ordre_paiement', 'creer_paiement_wizard_form_view')
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
                        'default_invoice_id': self.invoice_id.id,
                        'default_mode_paiement_id': self.mode_paiement_id.id,
                        'default_communication': self.objet,
                        },
            'target': 'new',
        }
# 'default_mode_paiement_id': self.mode_paiement_id.id

    def print_ordre_paiement(self):
        return self.env.ref('ordre_paiement.act_ordre_paiement').report_action(self)

