# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError
from datetime import datetime


class HrMissionautorisationWizard(models.TransientModel):
    _name = 'hr.mission.autorisation.wizard'
    _description = u'Autorisation vehicule'

    mission_id = fields.Many2one('hr.mission', string='Mission', readonly=True, required=True, )
    auto = fields.Boolean('acceptation/refus')
    employee = fields.Char('Autorisation pour', readonly=True)
    vehicule_id = fields.Many2one('fleet.vehicle', string='Véhicule', required=True)
    avec_chauffeur = fields.Boolean('Avec chauffeur')
    chauffeur_id = fields.Many2one('hr.employee', string='Chauffeur', check_company=False)
    motif_refus = fields.Text('Motif de refus')

    def action_autoriser(self):
        self.mission_id.vehicule_id = self.vehicule_id.id
        self.mission_id.avec_chauffeur = self.avec_chauffeur
        self.mission_id.chauffeur_id = self.chauffeur_id.id
        self.mission_id.autorise_par_id = self.env.user.id
        self.mission_id.autorise_date = datetime.now()
        self.mission_id.state = 'planned'

    def action_refuser(self):
        if self.motif_refus:
            self.mission_id.motif_refus = self.motif_refus
            self.mission_id.state = 'cancel'
            self.mission_id.autorise_par_id = self.env.user.id
            self.mission_id.autorise_date = datetime.now()
        else:
            raise UserError(_("Veuillez saisir le motif de refus"))
