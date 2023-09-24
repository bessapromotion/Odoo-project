# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Company(models.Model):
    _inherit = 'res.company'

    num_cnas = fields.Char('Numéro d\'adérant CNAS')
