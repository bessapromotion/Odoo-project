# -*- coding: utf-8 -*-

from odoo import models, fields


class Users(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    hubspot = fields.Char('HubSpot Owner name')
