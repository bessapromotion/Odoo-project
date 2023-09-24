from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    def compute_mt_encaisse(self):
        for rec in self:
            if rec.order_id:
                for ech in self.order_id.echeancier_ids:
                    if ech.name == '1':
                        rec.mt_encaisse_v = ech.montant
                        print('rec.mt_encaisse if', rec.mt_encaisse_v)
                    else:
                        rec.mt_encaisse_v = 0
            else:
                rec.mt_encaisse_v = 0

    def compute_p(self):
        for rec in self:
            rec.p = 1 / 100

    mt_encaisse_v = fields.Float(compute='compute_mt_encaisse', string='M. encaissé à la vente', store=True)
    taux_encaisse_v = fields.Float(compute='compute_mt_encaisse', string='M. encaissé à la vente', store=True)
    p = fields.Float(compute='compute_p', string='taux', store=True,group_operator="sum")
