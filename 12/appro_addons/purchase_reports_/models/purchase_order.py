# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import conversion


class PurchaseOrder(models.Model):
    _name    = 'purchase.order'
    _inherit = 'purchase.order'

    @api.one
    @api.depends('order_line')
    def _display_Number_To_Word(self):
        self.montant_lettre = conversion.conversion(self.amount_total)

    project_id       = fields.Many2one('project.project', string='Projet', readonly=1, states={'draft': [('readonly', False)]} )
    mode_paiement_id = fields.Many2one('payment.mode', string='Mode de paiement')
    montant_lettre   = fields.Text(compute=_display_Number_To_Word, string='Montant lettre')
    journal_id       = fields.Many2one('account.journal', string='Compte bancaire')
    rib              = fields.Char(related='journal_id.rib')
