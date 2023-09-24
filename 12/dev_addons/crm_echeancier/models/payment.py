# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import conversion


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    @api.depends('amount')
    def _display_number_to_word(self):
        for rec in self:
            rec.amount_lettre = conversion.conversion(rec.amount)

    echeance_id      = fields.Many2one('crm.echeancier', string='Echeance')
    project_id       = fields.Many2one(related='echeance_id.project_id', string='Projet')
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement')
    doc_payment_id   = fields.Many2one('payment.doc', string=u'Numéro')
    domiciliation    = fields.Char(related='doc_payment_id.domiciliation', string='Domiciliation', readonly=0)
    ordonateur       = fields.Char(related='doc_payment_id.ordonateur', string='Ordonateur', readonly=1)
    date             = fields.Date(related='doc_payment_id.date', string=u'Date chèque', readonly=1)
    paiement_concretisation = fields.Boolean('Paiement de concretisation')
    cheque_objet = fields.Selection(related='doc_payment_id.objet', string='Objet de Chèque', readonly=1)
    cheque_type = fields.Selection(related='doc_payment_id.type', string='Type de Chèque', readonly=1)
    # objet = fields.Char('Motif de paiement')
    partner_reference = fields.Char(u'Référence client', readonly=1, states={'open': [('readonly', False)]})
    observation = fields.Char('Observation')
    amount_lettre    = fields.Char(compute=_display_number_to_word, string='Montant en lettres', readonly=1)
