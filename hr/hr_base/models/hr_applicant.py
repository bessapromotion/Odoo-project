# -*- coding: utf-8 -*-

from odoo import fields, models, api


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    @api.depends('stage_id')
    def _compute_is_penultimate_stage(self):
        for rec in self:
            if rec.stage_id.id == self.env['hr.recruitment.stage'].search([])[-2].id:
                rec.is_penultimate_stage = True
            else:
                rec.is_penultimate_stage = False

    is_penultimate_stage = fields.Boolean(compute="_compute_is_penultimate_stage", store=True)
