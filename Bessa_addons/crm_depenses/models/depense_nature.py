# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _


class DepenseNature(models.Model):
    _name = 'depense.nature'
    _description = u'Nature de Depense '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char('Nom')
    depense_ids = fields.One2many('crm.depense', 'nature_id', string=u'Depenses')
