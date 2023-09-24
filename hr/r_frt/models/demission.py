# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from datetime import date


class Demission(models.Model):
    _inherit = 'hr.demission'

    frt_id = fields.Many2one('hr.frt', string='FRT', readonly=1, )

    def action_validate(self):
        super(Demission, self).action_validate()
        motif = self.env['hr.frt.motif'].search([('code', '=', 'DMS')])
        frt = self.env['hr.frt'].create({
            'employe_id': self.employe_id.id,
            'contract_id': self.contract_id.id,
            'demission_id': self.id,
            'motif_id': motif[0].id,
            'company_id': self.company_id.id,
            'date_effet': self.date_depart,
        })
        self.frt_id = frt
