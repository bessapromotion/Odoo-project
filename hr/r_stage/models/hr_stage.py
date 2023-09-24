# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    stages_ids = fields.One2many('hr.employee.stage', 'employee_id')


class HrEmployeeStage(models.Model):
    _name = 'hr.employee.stage'

    @api.depends('date_start', 'date_end')
    def compute_duree_stage(self):
        for rec in self:
            rec.duree = 0
            if rec.date_end and rec.date_start:
                rec.duree = (rec.date_end - rec.date_start).days + 1

    employee_id = fields.Many2one('hr.employee', check_company=True)
    date_start = fields.Date(string=u'Date debut')
    date_end = fields.Date(string=u'Date fin')
    duree = fields.Integer(compute='compute_duree_stage', string='Durée en jours')
    description_stage = fields.Text(string=u'Description')

    def action_print_att_stage(self):
        return self.env.ref('r_stage.act_report_att_stage').report_action(self)
