# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductFamille(models.Model):
    _name = 'product.famille'
    _description = 'Famille de produit'

    @api.depends('product_ids')
    def _product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    name = fields.Char('Famille de produit', required=True)
    code = fields.Char('Code', size=1, required=True)
    product_ids = fields.One2many('product.template', 'famille_id', string='Produits')
    product_count = fields.Integer(compute=_product_count, string='Nombre produits')
    sous_famille_ids   = fields.One2many('product.sousfamille', 'famille_id')

    _sql_constraints = [ ('name_uniq', 'unique (name)', "Famille existe déjà !")]


class ProductSousFamille(models.Model):
    _name = 'product.sousfamille'
    _description = 'Sous Famille de produit'

    @api.depends('product_ids')
    def _product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    name = fields.Char('SousFamille de produit', required=True)
    code = fields.Char('Code', size=2, required=True)
    sequence = fields.Char('Sequence', size=2, required=True)
    type = fields.Char('Type', size=1, required=True)
    famille_id = fields.Many2one('product.famille', string='Famille')
    product_ids = fields.One2many('product.template', 'sousfamille_id', string='Produits')
    product_count = fields.Integer(compute=_product_count, string='Nombre produits')

    _sql_constraints = [ ('name_uniq', 'unique (name)', "Sous Famille existe déjà !")]
