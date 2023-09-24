# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import date
from lxml import etree


class depenseTag(models.Model):
    _name = 'depense.tag'
    _description = 'Tags'

    name = fields.Char('Tag', required=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag existe deja !"),
    ]

