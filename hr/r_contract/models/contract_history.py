# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from collections import defaultdict


class ContractHistory(models.Model):
    _inherit = 'hr.contract.history'

    @api.depends('employee_id.contract_ids')
    def _compute_contract_ids(self):
        sorted_contracts = self.mapped('employee_id.contract_ids').sorted('date_start', reverse=True)

        mapped_employee_contracts = defaultdict(lambda: self.env['hr.contract'])
        for contract in sorted_contracts:
            # if contract.state != 'cancel':
            mapped_employee_contracts[contract.employee_id] |= contract

        for history in self:
            history.contract_ids = mapped_employee_contracts[history.employee_id]
