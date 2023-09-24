# -*- coding: utf-8 -*-

from odoo import models, fields


class MiseEnDemeureMotif(models.Model):
    _name = 'hr.demeure.motif'
    _description = 'Motif de la mise en demeure'

    name = fields.Char('Motif de la mise en demeure')
    description = fields.Text('Description')
