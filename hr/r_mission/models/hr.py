# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    @api.depends('missions_ids')
    def _nbr_mission(self):
        for rec in self:
            rec.nbr_mission = len(rec.missions_ids)

    missions_ids = fields.One2many('hr.mission.employee', 'name', string='Missions')
    nbr_mission  = fields.Integer(compute=_nbr_mission, string='Nombre de missions')
