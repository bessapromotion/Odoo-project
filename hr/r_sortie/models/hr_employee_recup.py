# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError


class Recup(models.Model):
    _name = 'hr.employee.recup'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Recuperation'

    @api.depends('date_debut', 'date_fin')
    def compute_duree_recup(self):
        for rec in self:
            rec.duree = 0
            if rec.date_fin and rec.date_debut:
                rec.duree = (rec.date_fin - rec.date_debut).days + 1

    name = fields.Char()
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', 'Validé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=1,
                                 states={'draft': [('readonly', False)], }, check_company=True)
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company,
                                 readonly=True)
    job_id = fields.Many2one(related='employe_id.job_id', string='Fonction')
    department_id = fields.Many2one(related='employe_id.department_id', string='Service')
    parent_id = fields.Many2one(related='employe_id.parent_id', string='Responsable Hiérarchique')
    remplacant_id = fields.Many2one('hr.employee', string='Remplaçant', required=False, readonly=1,
                                    states={'draft': [('readonly', False)], }, check_company=True)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    duree = fields.Integer('Durée en jour', compute='compute_duree_recup', states={'done': [('readonly', True)]})

    date_debut = fields.Datetime('Date début', required=True, default=datetime.now(), readonly=1,
                                 states={'draft': [('readonly', False)]})
    date_fin = fields.Datetime('Date fin', required=True, default=datetime.now(), readonly=1,
                               states={'draft': [('readonly', False)]})
    motif = fields.Text('Motif')

    def action_validate(self):
        for rec in self:
            rec.state = 'valid'
            rec.name = self.env['ir.sequence'].get('hr.employee.recup') or '/'
            self.env['hr.employee.historique'].create({
                'employe_id': rec.employe_id.id,
                'document': u'Bon de récuperation',
                'numero': rec.name,
                'date_doc': date.today(),
                'user_id': self.env.user.id,
                'note': u'Document joint à la fiche employé',
                'model_name': 'hr.employee.sortie',
                'model_id': rec.id,
            })

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
