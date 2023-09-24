# -*- coding: utf-8 -*-

from odoo import models, fields


class Job(models.Model):
    _name = 'hr.job'
    _inherit = 'hr.job'

    evaluation = fields.Boolean('Evaluation aprés expiration contrat', default=True)
