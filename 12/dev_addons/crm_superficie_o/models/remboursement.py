# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmRemboursement(models.Model):
    _inherit = 'crm.remboursement'

    superficie_id = fields.Many2one('crm.superficie', string='Changement superficie', readonly=1)
