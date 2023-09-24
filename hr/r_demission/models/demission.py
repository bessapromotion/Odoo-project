# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class Demission(models.Model):
    _name = 'hr.demission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Demission'

    state = fields.Selection([('draft', 'Nouveau'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    name = fields.Char(u'Numéro', default='/', readonly=1)
    employe_id = fields.Many2one('hr.employee', string='Employé', required=True,
                                 readonly=True, states={'draft': [('readonly', False)]}, check_company=True)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1)
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    job_id = fields.Many2one(related='employe_id.job_id', string='Fonction', readonly=1)
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    date_demission = fields.Date(u'Date de démission', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]})
    date_reception = fields.Date(u'Date de réception', required=True, readonly=True, default=date.today(),
                                 states={'draft': [('readonly', False)]})
    date_depart = fields.Date(u'Date de départ', required=True, readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company,
                                 readonly=True, states={'draft': [('readonly', False)]})
    note = fields.Text('Note')
    contract_id = fields.Many2one('hr.contract', string='Contrat', readonly=1,
                                  states={'draft': [('readonly', False)], 'progress': [('readonly', False)]})
    preavis = fields.Char('Durée préavis', related='contract_id.preavis',store=True)
    uom_preavis = fields.Selection([('jours', 'jours'), ('mois', 'mois')], default='mois',
                                   related='contract_id.uom_preavis')

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id.contract_id:
                rc.contract_id = rc.employe_id.contract_id.id
            else:
                contr = self.env['hr.contract'].search([('employee_id', '=', self.employe_id.id),
                                                        ('state', 'not in', ('draft', 'cancel'))])
                if contr:
                    rc.contract_id = contr[0].id
                else:
                    rc.contract_id = None

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('hr.demission') or '/'

        return super(models.Model, self).create(vals)

    def action_validate(self):
        self.state = 'done'
        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': 'Démlission',
            'numero': self.name,
            'date_doc': self.date_reception,
            'user_id': self.env.user.id,
            'note': '',
            'model_name': 'hr.demission',
            'model_id': self.id,
        })

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
