# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductPartner(models.Model):
    _name = 'product.partner'
    _description = u'Propriétaire du bien '
    _order = 'name desc'

    name = fields.Many2one('res.partner', string='Propriétaire', tracking=True)
    etat = fields.Selection(related='name.etat', string='Etat du client ODOO', tracking=True)
    origin = fields.Char("Document d'origine")
    type = fields.Char("Etiquette du client")
    product_id = fields.Many2one('product.template', string='Produit', store=True, tracking=True)
