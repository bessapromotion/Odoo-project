# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    remboursement_id = fields.Many2one('crm.remboursement', string='Remboursement', readonly=1, states={'draft': [('readonly', False)]})
    est_remboursement = fields.Boolean('est un remboursement')
