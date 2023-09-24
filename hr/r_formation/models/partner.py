# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    organisme_formation = fields.Boolean('Organisme de formation')
    organisme_agree = fields.Boolean('Agrée par l\'état')
    formateur = fields.Boolean('Formateur')

