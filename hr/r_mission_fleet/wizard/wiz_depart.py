# -*- coding: utf-8 -*-

from odoo import models, fields, _


class HrMissionDepartWizard(models.TransientModel):
    _name = 'hr.mission.depart.wizard'
    _description = u'Marquer le départ'

    mission_id = fields.Many2one('hr.mission', string='Mission', readonly=True, required=True, )

    km_depart = fields.Float(u'Kilométrage départ')
    date_depart = fields.Datetime(u'Date départ', required=True)
    vehicule_id = fields.Many2one(related='mission_id.vehicule_id', string='Véhicule')
    km_depart_actuel = fields.Float(related='mission_id.vehicule_id.odometer', string='Kilométrage actuel')

    def action_validate(self):
        self.mission_id.date_depart = self.date_depart
        self.mission_id.state = 'open'
        if self.vehicule_id:
            self.mission_id.km_depart = self.km_depart
            self.mission_id.vehicule_id.odometer = self.km_depart
            self.mission_id.vehicule_id._set_odometer()
