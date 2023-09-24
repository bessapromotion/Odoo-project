# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    amount_declared = fields.Monetary(u'Montant déclaré')
