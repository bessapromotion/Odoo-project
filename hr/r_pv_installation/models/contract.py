# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class Contract(models.Model):
    _inherit = 'hr.contract'

    hr_instalation_id = fields.Many2one('hr.installation', string='PV d\'instalation', readonly=True)

    def action_signer(self):
        super(Contract, self).action_signer()
        if self.type_avenant == 'Contrat':
            instalation_id = self.env['hr.installation'].create({
                'employe_id': self.employee_id.id,
                'contract_id': self.id,
                'company_id': self.company_id.id,
                'installation_date': self.date_start,
                's_date': self.date_start,
                'job_id': self.job_id.id,
            })
            instalation_id.action_validate()
            self.hr_instalation_id = instalation_id.id

    def action_print_pv(self):
        return self.hr_instalation_id.action_print()
