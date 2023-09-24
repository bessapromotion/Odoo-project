# -*- coding: utf-8 -*-

from odoo import models, fields #, api
# from odoo.exceptions import ValidationError


class ContractType(models.Model):
    _name               = 'hr.contract.type'
    _description        = 'Type contrat'
    _check_company_auto = True

    name          = fields.Char('Type de contrat')
    code          = fields.Char('Code', size=6)

    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)

