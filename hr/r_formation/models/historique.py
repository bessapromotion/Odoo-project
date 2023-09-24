# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class FormationBesoin(models.Model):
    _name = 'formation.session.historique'
    _inherit = ['mail.thread']
    _description = 'Historique des formations'

    formation_id = fields.Many2one('formation.session', 'Formation')
    theme_id = fields.Many2one('formation.theme', string='Theme de la Formation')
    formateur_id = fields.Many2one('res.partner', string='Formateur')
    employe_id = fields.Many2one('hr.employee', string='Employé', check_company=False)
    duree = fields.Integer('Durée en jour', )
    date_debut = fields.Date('Date debut', )
    date_fin = fields.Date('Date fin', )


class Employe(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    def get_nb_formation(self):
        formations = self.env['formation.session.historique'].search([('employe_id', '=', self.id), ])
        self.nbr_formation = len(formations)

    nbr_formation = fields.Integer(compute='get_nb_formation')
