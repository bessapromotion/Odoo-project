# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmployeeDepartment(models.Model):
    _inherit = 'hr.department'

    direction_id = fields.Many2one('hr.direction')


class EmployeeDerection(models.Model):
    _name = 'hr.direction'

    def count_employee(self):
        for rec in self:
            rec.nb_emp = 0
            employee = self.env['hr.employee'].search([('direction_id', '=', rec.id)])
            if employee:
                rec.nb_emp = len(employee)

    name = fields.Char('Direction', required=True)
    nb_emp = fields.Integer('Employés', compute='count_employee')
    department_ids = fields.One2many('hr.department', 'direction_id', string='Affectation')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)


class Employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    project_id = fields.Many2one('project.project', string='Affectation')
    direction_id = fields.Many2one('hr.direction', string='Direction')
    department_id = fields.Many2one('hr.department', 'Department',
                                    domain="[('direction_id', '=', direction_id)]")
