# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    famille_id = fields.Many2one('product.famille', string='Famille')
    sousfamille_id = fields.Many2one('product.sousfamille', string='SousFamille')
    etat_achat = fields.Selection([('bon', 'En cours'), ('reforme', 'A réformer')], default='bon',
                                  string='Etat du produit')

    def action_codifier(self):
        base_code = self.famille_id.code + self.sousfamille_id.code + self.sousfamille_id.sequence + self.sousfamille_id.type
        num = str(self.id).zfill(3)
        existing_count = self.env['product.product'].search_count([('default_code', '=', base_code + num)])

        while existing_count:
            num = str(int(num) + 1).zfill(3)
            existing_count = self.env['product.product'].search_count([('default_code', '=', base_code + num)])

        self.default_code = base_code + num


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    def action_codifier(self):
        base_code = self.product_tmpl_id.famille_id.code + self.product_tmpl_id.sousfamille_id.code + self.product_tmpl_id.sousfamille_id.sequence + self.product_tmpl_id.sousfamille_id.type
        num = str(self.id).zfill(3)
        existing_count = self.env['product.product'].search_count([('default_code', '=', base_code + num)])

        while existing_count:
            num = str(int(num) + 1).zfill(3)
            existing_count = self.env['product.product'].search_count([('default_code', '=', base_code + num)])

        self.default_code = base_code + num
