# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmDesistementDossier(models.Model):
    _name = 'crm.desistement.dossier'
    _description = 'Dossier desistement'

    name  = fields.Char('Piece')
