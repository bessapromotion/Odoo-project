from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def compute_mt_encaisse(self):
        for rec in self:
            if rec.nbr_echeances > 0:
                rec.mt_encaisse = rec.echeancier_ids[0].montant
            else:
                rec.mt_encaisse = 0

    mt_encaisse = fields.Float(compute='compute_mt_encaisse', string='M. encaissé à la vente', store=True)
