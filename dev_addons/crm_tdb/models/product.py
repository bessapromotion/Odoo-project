from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    def compute_taux_encaisse(self):
        for rec in self:

            rec.taux_encaisse_v = 0
            rec.mt_encaiss = 0
            if rec.order_id:
                # rec.taux_encaisse_v = rec.order_id.mt_encaisse
                rec.mt_encaiss = rec.order_id.mt_encaisse

    def compute_taux_encaisse_p(self):
        for rec in self:
            rec.taux_encaisse_p = 0
            if rec.list_price != 0:
                rec.taux_encaisse_p = rec.mt_encaiss * 100 / rec.list_price

    @api.depends('order_id')
    def get_price_product(self):
        for rec in self:
            # if rec.order_id:
            #     rec.valeur = rec.order_id.order_line[0].price_unit
            # else:
            rec.valeur = rec.list_price

    mt_encaiss = fields.Float(compute='compute_taux_encaisse', string='M. encaissé à la vente', store=True)
    taux_encaisse_v = fields.Float(compute='compute_taux_encaisse', string='M. encaissé à la vente', store=True)
    # p = fields.Float(compute='compute_p', string='taux', store=True, group_operator="sum")
    taux_encaisse_p = fields.Float(compute='compute_taux_encaisse_p', string='Taux', store=False,) #group_operator='avg'
    # prix_vente_devis = fields.Float(related='order_id.prix_vente_devis', string='M. Total', store=True)
    # valeur = fields.Monetary(string='Prix de vente', compute="get_price_product", store=True)
    state_order = fields.Selection(related='order_id.state', string='Etat BC', store=True)
    motif_annulation_order = fields.Selection(related='order_id.motif_annulation', string='Motif Annulation BC',
                                              store=True)
    origin_order = fields.Char(related='order_id.origin', string='Origin BC', store=True)
