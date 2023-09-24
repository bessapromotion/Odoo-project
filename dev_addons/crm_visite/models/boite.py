# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmVocale(models.Model):
    _name = 'crm.vocale'
    _description = 'Boite vocale'
    _order = 'heure_appel desc'

    name         = fields.Many2one('res.partner', string='Client')
    etat = fields.Selection(related='name.etat', string='Status')
    # status_client = fields.Many2one('utm.')
    date         = fields.Date('Date')
    phone        = fields.Char('Numéro de téléphone')
    user_id      = fields.Many2one('res.users', string='Commercial')
    heure_appel  = fields.Datetime('Heure appel')
    observation  = fields.Char('Observation')
    feedback = fields.Char('Feedback')
    tags_ids     = fields.Many2many('visite.tags', string='Etiquettes')
