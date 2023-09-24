# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _


class DepenseProject(models.Model):
    _name = 'depense.project'
    _description = u'Projet de Depense '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char('Nom')
    depense_ids = fields.One2many('crm.depense', 'project_id', string=u'Depenses')
    type_id = fields.Many2one('depense.type', string='Type')