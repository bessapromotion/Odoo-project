# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    @api.one
    @api.depends('product_ids')
    def _nbr_produitd(self):
        for rec in self:
            rec.nbr_produit = len(rec.product_ids)

    @api.one
    @api.depends('echeancier_ids')
    def _nbr_echeances(self):
        nbr = 0
        for rec in self:
            for line in rec.echeancier_ids:
                if line.state in ('draft', 'open',):
                    nbr += 1
            rec.nbr_echeances = nbr

    echeancier_ids = fields.One2many('crm.echeancier', 'partner_id', string='Echeancier')
    nbr_echeances  = fields.Integer(compute=_nbr_echeances, string='Echeances restantes')

    product_ids = fields.One2many('product.template', 'client_id', string='Produits')
    nbr_produit  = fields.Integer(compute=_nbr_produitd, string='Nombre produits')
