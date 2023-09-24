# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmDesistementDossier(models.Model):
    _name = 'crm.desistement.dossier'
    _description = 'Dossier desistement'

    name  = fields.Char('Piece')
    company_id = fields.Many2one('res.company', string=u'Société', index=True, readonly=0,
                                 default=lambda self: self.env.company)

