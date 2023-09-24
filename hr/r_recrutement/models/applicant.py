# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class HrContractHistory(models.Model):
    _inherit = 'hr.contract.history'

    def hr_contract_view_form_new_action(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('hr_contract.action_hr_contract')
        contract_type_id = False
        job_id = False
        duree_contract = 0
        salary_validate = 0
        applicant = self.env['hr.applicant'].search([('id', '=', self.employee_id.applicant1_id.id)])
        if len(applicant) > 0:
            contract_type_id = applicant[0].contract_type_id.id
            job_id = applicant[0].job_id.id
            duree_contract = applicant[0].duree_contract
            salary_validate = applicant[0].salary_validate
        action.update({
            'context': {''
                        'default_employee_id': self.employee_id.id,
                        'default_contract_type_id': contract_type_id,
                        'default_job_id': job_id,
                        'default_nbr_mois': duree_contract,
                        'default_wage': salary_validate,
                        },
            'view_mode': 'form',
            'view_id': self.env.ref('hr_contract.hr_contract_view_form').id,
            'views': [(self.env.ref('hr_contract.hr_contract_view_form').id, 'form')],
        })
        return action


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    applicant1_id = fields.Many2one('hr.applicant')


class Applicant(models.Model):
    _name = 'hr.applicant'
    _inherit = 'hr.applicant'

    salary_validate = fields.Float('Salaire validé')
    contract_type_id = fields.Many2one('hr.contract.type', "Type de Contrat", )
    code_contract = fields.Char(related='contract_type_id.code')
    duree_contract = fields.Integer('Durée de contrat en mois')
    date_promesse = fields.Date('Date proposition de contrat', default=date.today())
    date_prise_fonction = fields.Date('Date de prise de fonction', default=date.today())
    project_id = fields.Many2one('project.project', string='Affectation', )
    dossier_id = fields.Many2one('hr.dossier.model', string='Modele de dossier')
    file = fields.Binary(related='dossier_id.file', string='Dossier')

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'type': 'private',
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile,
                })
                applicant.partner_id = new_partner_id
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.partner_name or contact_name:
                employee_data = {
                    'default_name': applicant.partner_name or contact_name,
                    'default_project_id': applicant.project_id.id,
                    'default_email': applicant.email_from,
                    'default_telephone': applicant.partner_phone,
                    'default_job_id': applicant.job_id.id,
                    'default_job_title': applicant.job_id.name,
                    'default_address_home_id': address_id,
                    'default_department_id': applicant.department_id.id or False,
                    'default_address_id': applicant.company_id and applicant.company_id.partner_id
                                          and applicant.company_id.partner_id.id or False,
                    'default_work_email': applicant.department_id and applicant.department_id.company_id
                                          and applicant.department_id.company_id.email or False,
                    'default_work_phone': applicant.department_id.company_id.phone,
                    'form_view_initial_mode': 'edit',
                    'default_applicant_id': applicant.ids,
                    'default_applicant1_id': applicant.id,
                }

        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list')
        dict_act_window['context'] = employee_data
        return dict_act_window
