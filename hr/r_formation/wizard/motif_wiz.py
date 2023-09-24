# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime


class PlanningWizard(models.TransientModel):
    _name = 'formation.besoin.res.motif.wizard'
    _description = 'Planifier un placement'

    motif = fields.Text('Motif d\'annulation')
    res_id = fields.Many2one('formation.besoin.res')

    def action_create(self):
       self.res_id.motif = self.motif