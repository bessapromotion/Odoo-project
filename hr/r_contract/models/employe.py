# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    job_id = fields.Many2one(related='contract_id.job_id', store=True)
    last_contract_date = fields.Date(related='contract_id.date_end')
    contract_trial_start = fields.Date(related='contract_id.date_start', string='Date début périod d\'essai',
                                       store=True)
    contract_trial_end = fields.Date(related='contract_id.trial_date_end', string='Date fin périod d\'essai',
                                     store=True)
    contract_state = fields.Selection(related='contract_id.state', )
    contract_trial_state = fields.Selection(related='contract_id.trial_state', string='Etat de la période d\'essai',
                                            store=True)
