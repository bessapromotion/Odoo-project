# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class Historique(models.Model):
    _name = 'hr.employee.historique'
    _description = 'Historique'
    _order = 'create_date desc'

    name = fields.Char(u'Numéro', default='/', readonly=1)
    employe_id = fields.Many2one('hr.employee', string='Employé', check_company=True)
    document = fields.Char(u'Document')
    numero = fields.Char(u'Numéro document')
    date_doc = fields.Date(u'Date du document')
    date_prise_effet = fields.Date(u'Date prise effet')
    user_id = fields.Many2one('res.users', string='Etabli par', readonly=1)
    note = fields.Char('Note')
    model_name = fields.Char('Modele')
    model_id = fields.Integer('ID')
    num_embauche = fields.Integer('Num Embauche', default=1, readonly=1)
    company_id = fields.Many2one('res.company', string=u'Société', index=True, readonly=1,
                                 default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('hr.employee.historique') or '/'

        return super(models.Model, self).create(vals)

    def open_doc(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Action Name',
            'target': 'current',  # use 'current/new' for not opening in a dialog
            'res_model': self.model_name,
            'res_id': self.model_id,
            'view_type': 'form',
            'view_mode': 'form',
        }
