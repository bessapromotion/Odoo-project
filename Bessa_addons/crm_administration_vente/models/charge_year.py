# -*- coding: UTF-8 -*-


from odoo import models, fields


class ChargeYear(models.Model):
    _name = 'charge.year'
    _description = 'Charge year '

    name = fields.Char(u'Désignation année')
    order_ids = fields.Many2many("ordre.paiement.charge", string='Ordres', copy=False, readonly=True)
    paiement_ids = fields.Many2many("account.payment", string='Paiements', copy=False, readonly=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "année existe deja !"),
    ]