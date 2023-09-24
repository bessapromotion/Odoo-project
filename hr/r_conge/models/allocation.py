# -*- coding: utf-8 -*-

from odoo import models, fields


class Allocation(models.Model):
    _name = 'hr.leave.allocation'
    _inherit = 'hr.leave.allocation'

    source_id = fields.Many2one('hr.conge', string='Source')
