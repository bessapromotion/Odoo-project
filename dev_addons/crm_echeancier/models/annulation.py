# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import conversion


class CrmAnnulation(models.Model):
    _name = 'crm.annulation'
    _inherit = 'crm.annulation'

    echeancier_ids = fields.One2many(related='reservation_id.echeancier_ids', string='Echeancier')
