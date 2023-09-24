# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _


class DepenseType(models.Model):
    _name = 'depense.type'
    _description = u'Type de Depense '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char('Nom')
    depense_ids = fields.One2many('crm.depense', 'type_id', string=u'Depenses')
    sous_projects_ids = fields.One2many('depense.project', 'type_id')
