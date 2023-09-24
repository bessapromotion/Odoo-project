# -*- coding: utf-8 -*-

from odoo import models, fields


class SanctionType(models.Model):
    _name = 'hr.sanction.type'
    _description = 'Type de sanction'

    name = fields.Char('Type de sanction', required=1)
    description = fields.Text('Description')
    degre = fields.Selection([('1', '1er degré'), ('2', '2ème degré'), ('3', '3ème degré'), ],
                             string='Degré', default='1', required=1)


class FauteProfessionnelle(models.Model):
    _name = 'hr.faute.professionnelle'
    _description = 'Faute professionnelle'

    name = fields.Char('Faute professionnelle', required=1)
    description = fields.Text('Description')
    degre = fields.Selection([('1', '1er degré'), ('2', '2ème degré'), ('3', '3ème degré'), ],
                             string='Degré', default='1', required=1)
