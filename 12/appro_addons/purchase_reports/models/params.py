# -*- coding: utf-8 -*-

from odoo import models, fields


class ModePaiement(models.Model):
    _name = 'mode.paiement'
    _description = 'Mode de paiement'

    name = fields.Char('Mode de paiement')
