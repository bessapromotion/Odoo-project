# -*- coding: utf-8 -*-

from odoo import models, fields


class CongeRegion(models.Model):
    _name = 'hr.conge.region'
    _description = u'Paramètre congé'

    name     = fields.Char(u'Région', required=True)
    nbr_jour = fields.Float('Nombre de jours de congé par mois', default=2.5)


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    region_id = fields.Many2one('hr.conge.region', string=u'Région')
