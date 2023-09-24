# -*- coding: utf-8 -*-

from odoo import models, fields


class Company(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    nif = fields.Char('N.I.F')
    nis = fields.Char('N.I.S')
    ai = fields.Char('AI')
    rib = fields.Char('RIB')
    fax = fields.Char('FAX')


class ResPartnerBank(models.Model):
    _name = "res.partner.bank"
    _inherit = "res.partner.bank"

    rib = fields.Char('R.I.B')


class AccountJournal(models.Model):
    _name    = 'account.journal'
    _inherit = 'account.journal'

    rib = fields.Char(related='bank_account_id.rib')
