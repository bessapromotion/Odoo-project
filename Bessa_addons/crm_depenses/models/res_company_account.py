# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompanyAccount(models.Model):
    _name = 'res.company.account'
    _description = u'Comptes de société '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    type = fields.Selection([('banque', 'Banque'),
                             ('caisse', u'Caisse')], string='Type de compte', tracking=True, required=True)
    name = fields.Char(string=u'Compte Comptable', required=True)
    ref_bancaire = fields.Char(string=u'RIB')
    bank = fields.Selection([('AGB', 'AGB'),
                               ('BNA', u'BNA'),
                               ('BDL', 'BDL'),
                               ('BADR', 'BADR'),
                               ('CNEP 514', 'CNEP 514'),
                               ('CNEP 506', 'CNEP 506'),
                               ('TRUST', 'TRUST'),
                               ('BADR 2', 'BADR 2'),
                               ('CNEP', 'CNEP'),
                               ('CNEP BEN AK', 'CNEP BEN AK'),
                               ('CPA', 'CPA')], string='Banque', tracking=True)
    company_id = fields.Many2one('res.company', string=u'Société', required=True, readonly=1, default=lambda self: self.env.company)
    date = fields.Date('Date de creation', store=True, tracking=True)
    solde = fields.Monetary(string=u'Solde', store=True, tracking=True)
    currency_id = fields.Many2one(related='company_id.currency_id', string='Devise', store=True)
