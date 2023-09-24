# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrSNGrade(models.Model):
    _name = 'hr.sn.grade'
    _description = 'Grade'

    name  = fields.Char('Grade')


class Employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    sn_situation    = fields.Selection([('nonregularise', u'Non regularisé'), ('surcis', 'Surcis'), ('encours', 'En cours'), ('dispense', u'Dispensé'),  ('done', u'Rigularisé')], string='Situation service national')
    sn_motif_surcis = fields.Char('Motif surcis/disponse')
    sn_date_entree  = fields.Date(u'Date entrée')
    sn_date_sortie  = fields.Date(u'Date sortie')
    sn_date_fin_surcis  = fields.Date('Date fin surcis')
    sn_grade_id     = fields.Many2one('hr.sn.grade', string='Grade')

