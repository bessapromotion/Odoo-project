# -*- coding: utf-8 -*-

from odoo import models, fields


class Product(models.Model):
    _name    = 'product.template'
    _inherit = 'product.template'

    reservation_id = fields.Many2one('crm.reservation', string='Réservation', readonly=True)
