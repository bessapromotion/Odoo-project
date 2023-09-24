# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = 'crm.lead'

    project_id     = fields.Many2one('project.project', string='Projet')
