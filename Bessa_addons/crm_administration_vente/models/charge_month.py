# -*- coding: UTF-8 -*-


from odoo import models, fields


class ChargeMonth(models.Model):
    _name = 'charge.month'
    _description = 'Charge month '

    name = fields.Char(u'Désignation mois')
    order_ids = fields.Many2many("ordre.paiement.charge", string='Ordres', copy=False, readonly=True)
    paiement_ids = fields.Many2many("account.payment", string='Paiements', copy=False, readonly=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "mois existe deja !"),
    ]