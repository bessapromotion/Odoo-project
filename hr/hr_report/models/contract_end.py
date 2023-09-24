# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta


class ContractEnd(models.Model):
    _name = 'hr.contract.end'

    employe_id = fields.Many2one('hr.employee')
    contract_id = fields.Many2one('hr.contract')
    company_id = fields.Many2one('res.company', )
    date_end = fields.Date('Date fin de contrat')
    delai = fields.Integer('Nombre de jour')

    date_start = fields.Date('Date début de contrat')
    state = fields.Selection('Etat de contrat', related='contract_id.state')

    def init(self):
        ems = self.env['hr.contract.end'].search([])
        ems.unlink()
        contracts = self.env['hr.contract'].search([
            ('state', '=', 'open'),
            ('date_end', '>', fields.Date.to_string(date.today())),
            ('date_end', '<', fields.Date.to_string(date.today() + relativedelta(days=15)))
        ])
        for rec in contracts:
            self.env['hr.contract.end'].create({
                'employe_id': rec.employee_id.id,
                'contract_id': rec.id,
                'company_id': rec.company_id.id,
                'date_end': rec.date_end,
                'date_start': rec.date_start,
                'delai': (rec.date_end - date.today()).days,
            })
