# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import date
from lxml import etree


class OperationBancaire(models.Model):
    _name = 'operation.bancaire'
    _inherit = 'operation.bancaire'

    caisse_id = fields.Many2one('crm.caisse', string='Caisse', store=True)


