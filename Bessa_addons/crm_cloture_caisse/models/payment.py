# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    caisse_id = fields.Many2one('crm.caisse', string='Caisse')
