# -*- coding: utf-8 -*-

from odoo import models, fields, api
# from odoo.exceptions import ValidationError


class ContractModel(models.Model):
    _name               = 'hr.contract.modele'
    _description        = 'Modele contrat'
    _check_company_auto = True

    name    = fields.Char(u'Modèle de contrat')
    type_id = fields.Many2one('hr.contract.type', string='Type de contrat', required=True, check_company=True)
    code = fields.Char(related="type_id.code")

    # article_lines = fields.One2many('hr.contract.article.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    article_lines = fields.One2many('hr.contract.modele.article.line', 'modele_id', string='Articles', copy=True)

    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)
