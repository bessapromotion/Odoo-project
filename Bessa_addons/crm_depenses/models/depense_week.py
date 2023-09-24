# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _



class DepenseWeek(models.Model):
    _name = 'depense.week'
    _description = u'Semaine de Depense '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char('Numero')
    #depense_ids = fields.One2many('crm.depense', 'week_id', string=u'Depenses')
