# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date


class Reintegration(models.Model):
    _name = 'hr.reintegration'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Réintegration'

    name = fields.Char(u'Numéro', default='/')  # , readonly=1)
    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, check_company=True)
    user_id = fields.Many2one('res.users', string='Etabli par', readonly=1, default=lambda self: self.env.user)
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    job_id = fields.Many2one('hr.job', string='Fonction', required=True)
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    date_reintegration = fields.Date(u'Date de réintégration', required=True)
    contract_id = fields.Many2one('hr.contract', string='Contrat de travail')
    modele_id = fields.Many2one('hr.contract.modele', string=u'Modèle de contrat', required=True)
    department_id = fields.Many2one('hr.department', string=u'Département', required=True)
    contract_type_id = fields.Many2one('hr.contract.type', string=u'Type contrat', required=True)

    note = fields.Text('Note')
    state = fields.Selection([('draft', 'Nouveau'),
                              ('done', u'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    company_id = fields.Many2one('res.company', string=u'Société', index=True, readonly=1,
                                 default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('hr.reintegration') or '/'

        return super(models.Model, self).create(vals)

    def action_validate(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def create_contract(self):
        self.employe_id.active = True
        self.employe_id.num_embauche += 1
        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': u'Reintegration',
            'numero': self.name,
            'date_doc': date.today(),
            'user_id': self.env.user.id,
            'note': u'Document joint à la fiche de reintegrartion',
            'model_name': 'hr.reintegration',
            'model_id': self.id,
        })
        contrat = self.env['hr.contract'].create({
            'employee_id': self.employe_id.id,
            'job_id': self.job_id.id,
            'num_embauche': self.employe_id.num_embauche,
            'date_etablissement': datetime.now(),
            'user_id': self.user_id.id,
            'structure_type_id': 1,
            'modele_id': self.modele_id.id,
            'contract_type_id': self.contract_type_id.id,
            'department_id': self.department_id.id,
            'date_entree': self.date_reintegration,
            'date_start': self.date_reintegration,
            'date_end': self.date_reintegration,
            'wage': 1,
        })
        self.contract_id = contrat.id
        contrat._onchange_modele_id()

        return {
            'name': 'Contrat de travail',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.contract',
            'target': 'current',
            'res_id': contrat.id,
        }
