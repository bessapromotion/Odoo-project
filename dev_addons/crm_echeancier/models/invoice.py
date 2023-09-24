# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    echeance_ok  = fields.Boolean(u'Echéances créées')
