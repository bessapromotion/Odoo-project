# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError


class Sortie(models.Model):
    _name = 'hr.employee.sortie'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Bon de sortie'

    name = fields.Char()
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', 'Validé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=1,
                                 states={'draft': [('readonly', False)], }, check_company=True)
    date = fields.Date('Date', required=True, default=datetime.now(), readonly=1,
                       states={'draft': [('readonly', False)]})
    job_id = fields.Many2one(related='employe_id.job_id', string='Fonction')
    department_id = fields.Many2one(related='employe_id.department_id', string='Service')
    parent_id = fields.Many2one(related='employe_id.parent_id', string='Responsable Hiérarchique')
    remplacant_id = fields.Many2one('hr.employee', string='Remplaçant', required=False, readonly=1,
                                    states={'draft': [('readonly', False)], }, check_company=True)

    date_sortie = fields.Datetime('Heure de sortie', required=True, default=datetime.now(), readonly=1,
                                  states={'draft': [('readonly', False)]})
    date_retour = fields.Datetime('Heure de retour', required=False, readonly=1,
                                  states={'draft': [('readonly', False)]})
    motif = fields.Text('Motif')
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company,
                                 readonly=True)

    def action_validate(self):
        for rec in self:
            rec.state = 'valid'
            rec.name = self.env['ir.sequence'].get('hr.employee.sortie') or '/'
            self.env['hr.employee.historique'].create({
                'employe_id': rec.employe_id.id,
                'document': u'Bon de sortie',
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
