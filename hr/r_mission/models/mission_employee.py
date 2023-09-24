# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class MissionEmployee(models.Model):
    _name = 'hr.mission.employee'
    _description = 'Missionnaire'

    name = fields.Many2one('hr.employee', string='Messionnaire', check_company=False)
    numero = fields.Char(related='mission_id.name', string='Numéro', readonly=1)
    matricule = fields.Char(related='name.matricule', string='Matricule', readonly=1)
    job_id = fields.Many2one('hr.job', string='Fonction')
    image = fields.Binary(related='name.image_1920', string='Photo')
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company,
                                 readonly=True)
    date = fields.Date(related='mission_id.date', string='Date etablissement', readonly=1)
    date_depart = fields.Datetime(related='mission_id.date_depart', string='Date de départ', readonly=1)
    date_retour = fields.Datetime(related='mission_id.date_retour', string='Date de retour', readonly=1)
    destination = fields.Char(related='mission_id.destination', string='Se rendre à', readonly=1)
    motif = fields.Char(related='mission_id.motif', string='Motif de départ', readonly=1)
    moyen_id = fields.Many2one(related='mission_id.moyen_id', string='Moyen de transport', readonly=1)
    state = fields.Selection(related='mission_id.state', string='Etat', readonly=1)

    mission_id = fields.Many2one('hr.mission', string='Ordre mission')

    @api.onchange('name')
    def onchange_employee(self):
        for rc in self:
            if rc.name:
                rc.job_id = rc.name.job_id.id
            else:
                rc.job_id = None

    @api.model
    def create(self, vals):
        vals['job_id'] = self.env['hr.employee'].browse(vals.get('name')).job_id.id

        return super(models.Model, self).create(vals)

    def action_print(self):
        return self.env.ref('r_mission.act_report_ordre_mission_employee').report_action(self)
