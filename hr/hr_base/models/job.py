# -*- coding: utf-8 -*-

from odoo import models, fields


class Job(models.Model):
    _name = 'hr.job'
    _inherit = 'hr.job'

    code = fields.Char('Code')
    preavis = fields.Char('Durée préavis')
    uom_preavis = fields.Selection([('jours', 'jours'), ('mois', 'mois')], default='mois')
    csp_id = fields.Many2one('hr.csp', string='Cat. SocioProfessionnelle')
    mission_ids = fields.One2many('hr.job.mission', 'job_id', string='Missions')

    _sql_constraints = [('name_uniq', 'unique (name)', "Poste existe deja !"), ]


class JobMission(models.Model):
    _name = 'hr.job.mission'
    _description = 'Mission'

    name = fields.Char('Mission')
    job_id = fields.Many2one('hr.job', string='Poste')
