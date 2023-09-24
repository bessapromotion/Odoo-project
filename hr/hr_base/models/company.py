# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    num_employeur = fields.Char('Numéro employeur')
    matricule_employeur = fields.Integer('Matricule employeur')
