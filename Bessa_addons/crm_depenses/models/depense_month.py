# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _


class DepenseMonth(models.Model):
    _name = 'depense.month'
    _description = u'Mois de Depense '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char('Numero')
    #depense_ids = fields.One2many('crm.depense', 'month_id', string=u'Depenses')
