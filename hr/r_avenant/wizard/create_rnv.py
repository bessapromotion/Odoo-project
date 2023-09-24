# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
import datetime
from datetime import date
from odoo.exceptions import UserError


class RnvContractWizard(models.TransientModel):
    _name = 'rnv.contract.wizard'

    employee_id = fields.Many2one('hr.employee', string='Employé', readonly=1, check_company=True)
    contract_id = fields.Many2one('hr.contract', string='Contrat initial', readonly=1)
    job_id = fields.Many2one('hr.job', string='Fonction')
    date_start = fields.Date(u'Date début', default=fields.Date.today)
    date_end = fields.Date(u'Date fin', )
    nbr_mois = fields.Integer('Durée contrat (en mois)')
    wage = fields.Float('Nouveau salaire')
    categorie = fields.Char(u'Catégorie')
    section = fields.Char('Section')
    trial_nbr_mois = fields.Integer("Durée periode d'essai (en mois)")

    def action_create(self):
        contract = self.env['hr.contract'].create({
            'employee_id': self.employee_id.id,
            'num_embauche': self.contract_id.num_embauche,
            'parent_id': self.contract_id.id,
            'department_id': self.contract_id.department_id.id,
            'date_entree': self.contract_id.date_entree,
            'user_id': self.env.user.id,
            'date_etablissement': self.contract_id.date_etablissement,
            'type_avenant': 'Contrat',
            'type_id': self.contract_id.type_id.id,
            'job_id': self.job_id.id,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'categorie': self.categorie,
            'hr_responsible_id': self.contract_id.hr_responsible_id.id,
            'section': self.section,
            'nbr_mois': self.nbr_mois,
            'wage': self.wage,
            'preavis': self.contract_id.preavis,
            'type_salaire': self.contract_id.type_salaire,
            'trial_nbr_mois': self.trial_nbr_mois,
            'trial_date_end': self.date_start + relativedelta(months=self.trial_nbr_mois),
            'type_contract': 'rnv',

            # NEW EDITS
            'modele_id': self.contract_id.modele_id.id,
            'structure_type_id': self.contract_id.structure_type_id.id if self.contract_id.structure_type_id else False,
        })
        contract._fill_articles()
        self.contract_id.state = 'close'
        self.employee_id.contract_id = contract.id
        history = self.env['hr.contract.history'].search([('employee_id', '=', self.employee_id.id)])
        if history:
            history[0].contract_ids = [(0, 0, {'id': self.contract_id.id}), ]
        return {
            'name': 'Contrat',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.contract',
            'target': 'current',
            'res_id': contract.id,
        }

    @api.onchange('date_start', 'nbr_mois')
    def _onchange_date_contract(self):
        for rc in self:
            if rc.date_start and rc.nbr_mois != 0:
                rc.date_end = rc.date_start + relativedelta(months=+rc.nbr_mois) - relativedelta(days=1)

    @api.onchange('date_start', 'date_end')
    def _onchange_dates_contract(self):
        if self.date_start and self.date_end and self.date_end >= self.date_start:
            diff = relativedelta(self.date_end, self.date_start)
            self.nbr_mois = diff.years * 12 + diff.months + 1
