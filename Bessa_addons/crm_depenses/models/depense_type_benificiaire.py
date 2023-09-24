# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import date
from lxml import etree


class depenseTypeBenificiaire(models.Model):
    _name = 'depense.type.benificaire'
    _description = 'Type Benificiaire'

    name = fields.Char('Type benificiaire', required=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag existe deja !"),
    ]

