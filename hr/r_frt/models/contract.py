# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from datetime import date


class Contract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def create_frt(self):
        contracts = self.search([
            ('state', '=', 'close'), ('type_id_code', '=', 'CDD'),
            ('date_end', '=', fields.Date.to_string(date.today()))
        ])
        motif = self.env['hr.frt.motif'].search([('code', '=', 'FDC')])
        for rec in contracts:
            frt = self.env['hr.frt'].create({
                'employe_id': rec.employee_id.id,
                'contract_id': rec.id,
                'motif_id': motif[0].id,
                'date_effet': rec.date_end,
            })
            article_lines = self.env['hr.frt.motif.line'].search([('motif_id', '=', motif.id)])
            for line in article_lines:
                self.env['hr.frt.article.line'].create({
                    'article_id': line.name.id,
                    'frt_id': frt.id,
                })
            frt.action_validate()
            rec.employee_id.active = 0
