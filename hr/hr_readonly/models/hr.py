# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError
from lxml import etree
import json


class Hr(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    @api.depends('contract_ids')
    def _nbr_contrat(self):
        for rec in self:
            rec.nbr_contrat = len(rec.contract_ids)

    nbr_contrat = fields.Integer(compute=_nbr_contrat)

    def copy(self, default=None):
        raise UserError(_(
            'La fonction duplication a été désactivée !'))
