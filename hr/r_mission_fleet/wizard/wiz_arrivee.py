# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class HrMissionArriveeWizard(models.TransientModel):
    _name = 'hr.mission.arrivee.wizard'
    _description = u'Marquer l\'arrivée'

    mission_id = fields.Many2one('hr.mission', string='Mission', readonly=True, required=True, )

    km_arrivee = fields.Float(u'Kilométrage arrivée')
    date_arrivee = fields.Datetime(u'Date arrivée', required=True)
    vehicule_id = fields.Many2one(related='mission_id.vehicule_id', string='Véhicule')
    km_arrivee_actuel = fields.Float(related='mission_id.vehicule_id.odometer', string='Kilométrage actuel')

    def action_validate(self):
        if self.km_arrivee <= self.mission_id.km_depart and self.vehicule_id:
            raise UserError(
                _("Veuillez mettre à jour le kilométrage du véhicule avant de valider l'arrivée"))

        self.mission_id.date_retour = self.date_arrivee
        self.mission_id.state = 'done'

        if self.vehicule_id:
            self.mission_id.km_arrivee = self.km_arrivee
            self.mission_id.vehicule_id.odometer = self.km_arrivee
            self.mission_id.vehicule_id._set_odometer()
