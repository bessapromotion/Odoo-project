# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _name    = 'res.partner'
    _inherit = 'res.partner'


    # les champs obligatoires
    type_pi = fields.Selection([('cin', u'Carte d\'identité nationale'),
                                ('permis', 'Permis de conduire'),
                                ('passport', 'Passport'),
                                ('autre', 'Autre')], String=u'Pièce identité', default='cin', required=1)
    num_pi = fields.Char(u'Numéro pièce d\'identité', required=1)
    # code_client = fields.Char('Code client', required=1)
    street = fields.Char(required=1)
    city = fields.Char(required=1)
    state_id = fields.Many2one("res.country.state", required=1)
    country_id = fields.Many2one('res.country', required=1)
    mobile = fields.Char(required=1)
    email = fields.Char(required=1)
