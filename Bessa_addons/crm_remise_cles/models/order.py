# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    changement_proprietaire_id = fields.One2many('changement.proprietaire', 'order_id',
                                                 string=u'Changement de propeiétaire',
                                                 tracking=True, store=True)

    changement_proprietaire = fields.Boolean('Changement', default=False)
