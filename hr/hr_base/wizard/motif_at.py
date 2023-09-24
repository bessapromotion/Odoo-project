# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import date


class MotifAttestationWizard(models.TransientModel):
    _name = 'motif.attestation.wizard'

    name = fields.Many2one('hr.employee', string='Employé', readonly=1, check_company=True)
    motif = fields.Char(u'Motif de délivrance', required=1)
    state = fields.Selection([('1', 'Saisi motif'), ('2', 'Impression')], default='1')
    user = fields.Char('User')

    def action_validate(self):
        self.name.motif_attestation = self.motif
        # self.name.user_print = self.env.user.date_emplacement
        self.state = '2'

        return self.env.ref('hr_base.act_report_attestation_travail').report_action(self.name.id)
