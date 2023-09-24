# -*- coding: utf-8 -*-

from odoo import models, fields


class FRTMotif(models.Model):
    _name = 'hr.frt.motif'
    _description = 'Motif Fin relation de travail'

    name = fields.Char('Motif de fin de relation de travail', required=1)
    code = fields.Char('Code', size=3, required=1)
    # reintegration = fields.Boolean(u'Autorise une réintegration')
    cntrl_date = fields.Boolean('Controle (Date prise effet < date fin contrat)')
    description = fields.Text('Description')
    article_lines = fields.One2many('hr.frt.motif.line', 'motif_id')


class FRTMotifLine(models.Model):
    _name = 'hr.frt.motif.line'

    motif_id = fields.Many2one('hr.frt.motif', string=u'Motif', )
    name = fields.Many2one('hr.frt.motif.article', string=u'Article', required=1)
