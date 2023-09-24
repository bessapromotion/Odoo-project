# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmLifecycle(models.Model):
    _name = 'crm.lifecycle'

    name = fields.Char('Etape hubspot')
    crm_stage_id = fields.Many2one('crm.stage', u'Mettre l\'opportunité a l\'etat')
    etat  = fields.Selection([('Prospect', 'Prospect'),
                              ('Potentiel', 'Potentiel'),
                              ('Réservataire', 'Réservataire'),
                              ('Acquéreur', 'Acquéreur'),
                              ('Locataire', 'Locataire'),
                              ], string=u'Mettre le client a l\'état', default='Prospect')

