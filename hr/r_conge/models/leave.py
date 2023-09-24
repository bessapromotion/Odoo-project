# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Leave(models.Model):
    _name = 'hr.leave'
    _inherit = 'hr.leave'

    @api.depends('date_from', 'date_to', 'employee_id')
    def _compute_number_of_days(self):
        for holiday in self:
            if holiday.date_from and holiday.date_to:
                holiday.number_of_days = (holiday.date_to - holiday.date_from).days + 1
            else:
                holiday.number_of_days = 0

    employee_remplacent_id = fields.Many2one('hr.employee', string='Remplaçant ', check_company=False)
