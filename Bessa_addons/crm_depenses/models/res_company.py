# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    account_ids = fields.One2many('res.company.account', 'company_id', string=u'Comptes')
