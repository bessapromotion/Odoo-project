# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrEmsWizard(models.TransientModel):
    _name = 'hr.ems.wizard'

    date_start = fields.Date(string=u'Date debut', required=1)
    date_end = fields.Date(string=u'Date fin', required=1)

    def action_appliquer(self):
        ems = self.env['hr.ems'].search([])
        ems.unlink()
        employees_contract = self.env['hr.contract'].search(
            [('date_entree', '>=', self.date_start), ('date_entree', '<=', self.date_end), ('state', '=', 'open'),
             ('type_contract', '=', 'new'), ])
        if employees_contract:
            for e in employees_contract:
                self.env['hr.ems'].create({
                    'employe_id': e.employee_id.id,
                    'type': 'contract',
                    'date_entree': e.date_entree,
                    'company_id': e.company_id.id,
                })
        employees_frt = self.env['hr.frt'].search(
            [('date_effet', '>', self.date_start), ('date_effet', '<', self.date_end),
             ('state', 'in', ['valid', 'done'])])
        if employees_frt:
            for e in employees_frt:
                self.env['hr.ems'].create({
                    'employe_id': e.employe_id.id,
                    'type': 'frt',
                    'date_sortie': e.date_effet,
                    'date_entree': e.contract_id.date_entree,
                    'company_id': e.contract_id.company_id.id,
                })
        view_id = self.env['ir.model.data']._xmlid_to_res_id('hr_report.hr_ems_tree_view')
        return {
            'name': 'EMS',
            'view_mode': 'form',
            'views': [(view_id, 'tree'), ],
            'res_model': 'hr.ems',
            'type': 'ir.actions.act_window',
        }
