# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class EvaluationDecision(models.Model):
    _name = 'hr.evaluation.decision'
    _description = 'Decision d Evaluation individuelle'

    name = fields.Char('Criter', required=True)
    description = fields.Text('Description')
    decision = fields.Selection([('FRT', 'FRT'), ('AVENANT', 'AVENANT'), ])


class EvaluationCriters(models.Model):
    _name = 'hr.evaluation.criters'
    _description = 'Criters d Evaluation individuelle'

    name = fields.Char('Criter', required=True)
    description = fields.Text('Description')
    type = fields.Many2many('hr.evaluation.criters.type')


class EvaluationCritersType(models.Model):
    _name = 'hr.evaluation.criters.type'
    _description = 'Type de criters d Evaluation individuelle'

    name = fields.Char('Type de Criter', required=True)
