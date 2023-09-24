# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime


class CongeOccasion(models.Model):
    _name = 'hr.conge.occasion'
    _description = 'Occasion'

    name      = fields.Char(u'Nom de l\'occasion', required=True)
    date_fixe = fields.Char(u'Mois-Jour', size=5)
    type = fields.Selection([('Nationale', 'Nationale'), ('Religieuse', 'Religieuse')], string='Type Occasion')


class CongeFerie(models.Model):
    _name = 'hr.conge.ferie'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Jours fériés de l\'année'

    name     = fields.Char(u'Année', size=4, required=True)
    date_ids = fields.One2many('hr.conge.ferie.date', 'annee_id')
    active   = fields.Boolean('Active', default=True)
    loaded   = fields.Boolean('chargé')

    def action_load(self):
        occasion = self.env['hr.conge.occasion'].search([])
        for rec in occasion:
            if rec.date_fixe:
                dt = datetime(int(self.name), int(rec.date_fixe[:2]), int(rec.date_fixe[3:]))
            else:
                dt = None

            self.env['hr.conge.ferie.date'].create({
                'name': rec.id,
                'date': dt,
                'annee_id': self.id,
            })
        self.loaded = True

    def unlink(self):
        self.date_ids.unlink()
        return super(models.Model, self).unlink()


class CongeFerieDate(models.Model):
    _name = 'hr.conge.ferie.date'
    _description = u'Jour férié'

    name     = fields.Many2one('hr.conge.occasion', string='Occasion', required=True)
    date     = fields.Date(u'Date')
    annee_id = fields.Many2one('hr.conge.ferie', string='Année')
