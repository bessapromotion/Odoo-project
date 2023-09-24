# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


class Contract(models.Model):
    _inherit = 'res.company'

    contract_represente = fields.Char('Représentée par')
    contract_represente_fonction = fields.Char('fonction')
