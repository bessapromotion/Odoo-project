# -*- coding: utf-8 -*-

from odoo import models, fields


class FormationTypologie(models.Model):
    _name = 'formation.typologie'
    _description = 'Typologie de formation'

    name        = fields.Char('Typologie', required=1)


class Categorie(models.Model):
    _name = 'formation.theme.categorie'
    _description = 'Categorie'

    name        = fields.Char('Categorie', required=1)


class Theme(models.Model):
    _name = 'formation.theme'
    _description = 'Theme'

    name         = fields.Char('Theme', required=1)
    categorie_id = fields.Many2one('formation.theme.categorie', string='Categorie')
    code         = fields.Char('Code')
