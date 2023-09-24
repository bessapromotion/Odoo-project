# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    maitre = fields.Char(string=u'Notaire')
    adresse_maitre = fields.Char(string=u'Adresse du Notaire')
