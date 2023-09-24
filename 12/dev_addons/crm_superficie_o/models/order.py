# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    superficie_id = fields.Many2one('crm.superficie', string='Changement superficie', readonly=1)
