# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta


class ContractTrial(models.Model):
    _name = 'hr.contract.trial'

    employe_id = fields.Many2one('hr.employee')
    contract_id = fields.Many2one('hr.contract')
    company_id = fields.Many2one('res.company', )
    trial_date_end = fields.Date('Date fin période d\'essai', )
    delai = fields.Integer('Nombre de jour', )

    trial_date_start = fields.Date('Date début période d\'essai', )
    trial_state = fields.Selection([('open', 'En cours'),
                                    ('renewed', 'Renouvelée'),
                                    ('expired', 'Expirée'),
                                    ('done', 'Clôturée'), ], string='Etat de la période d\'essai', default='open',
                                   readonly=False)

    def init(self):
        ems = self.env['hr.contract.trial'].search([])
        ems.unlink()
        contracts = self.env['hr.contract'].search([
            ('state', '=', 'open'),
            ('trial_date_end', '>', fields.Date.to_string(date.today())),
            ('trial_date_end', '<', fields.Date.to_string(date.today() + relativedelta(days=15)))
        ])
        for rec in contracts:
            self.env['hr.contract.trial'].create({
                'employe_id': rec.employee_id.id,
                'contract_id': rec.id,
                'company_id': rec.company_id.id,
                'trial_date_end': rec.trial_date_end,
                'trial_date_start': rec.trial_date_start,
                'trial_state': rec.trial_state,
                'delai': (rec.trial_date_end - date.today()).days,
            })
