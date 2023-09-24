# -*- coding: utf-8 -*-

from odoo import models, fields


class ModePaiement(models.Model):
    _name = 'payment.mode'
    _description = 'Mode de paiement'

    name = fields.Char('Mode de paiement')


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    mode_paiement_id = fields.Many2one('payment.mode', string='Mode de paiement')
    ordre_paiement_id = fields.Many2one('ordre.opaiement', string='Ordre de paiement')
