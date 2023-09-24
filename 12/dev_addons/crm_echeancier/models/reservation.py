# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import conversion


class CrmReservation(models.Model):
    _name = 'crm.reservation'
    _inherit = 'crm.reservation'

    @api.one
    @api.depends('amount_total')
    def _display_number_to_word(self):
        for rec in self:
            rec.montant_lettre = conversion.conversion(rec.amount_total)

    echeancier_ids = fields.One2many(related='order_id.echeancier_ids', string='Echeancier')
    currency_id = fields.Many2one(related='order_id.currency_id', string='Devise')
    amount_total = fields.Monetary(related='order_id.amount_untaxed', string='Total (HT)', currency_field='currency_id', readonly=True)
    amount_tva = fields.Monetary(related='order_id.amount_tax', string='Total TVA', currency_field='currency_id', readonly=True)
    total_paiement = fields.Monetary(related='order_id.total_paiement', string='Total paiement')
    montant_lettre = fields.Char(compute='_display_number_to_word', string='Montant lettre', readonly=1)
