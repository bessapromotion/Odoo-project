# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import conversion


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('amount_total')
    def _display_Number_To_Word(self):
        for rec in self:
            rec.montant_lettre = conversion.conversion(rec.amount_total)

    def compute_get_tax(self):
        self.taxe = ''
        t = []
        for rec in self.order_line:
            if rec.taxes_id.description not in t and not rec.display_type:
                t.append(rec.taxes_id.description)
                self.taxe = rec.taxes_id.description + ' ' + self.taxe

    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement')
    # project_id       = fields.Many2one('project.project', string='Projet', readonly=1, states={'draft': [('readonly', False)]} )
    montant_lettre = fields.Text(compute=_display_Number_To_Word, string='Montant lettre')
    journal_id       = fields.Many2one('account.journal', string='Compte bancaire')
    rib              = fields.Char(related='journal_id.rib')
    note = fields.Text()
    taxe = fields.Text(compute='compute_get_tax')
