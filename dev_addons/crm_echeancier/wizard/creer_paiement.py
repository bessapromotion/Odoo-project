# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class CreerPaiementWizard(models.TransientModel):
    _name = 'creer.paiement.wizard'
    _description = u'Créer le paiement'

    name = fields.Many2one('ordre.paiement', string='Ordre de paiement', required=1, readonly=1,
                           default=lambda self: self.env.context['active_id'])
    echeance_id = fields.Many2one(related='name.echeance_id', string='Echeance')
    company_id = fields.Many2one('res.company', u'Société', related='name.company_id', store=True)
    currency_id = fields.Many2one(related='name.currency_id')
    amount = fields.Monetary('Montant', currency_field='currency_id')
    amount_commercial = fields.Monetary('Montant', currency_field='currency_id')
    order_id = fields.Many2one(related='name.order_id', string='Commande', readonly=True)
    partner_id = fields.Many2one(related='name.partner_id', string='Client', readonly=True)

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])

    payment_date = fields.Date('Date', required=True, copy=False)
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement', required=True)
    communication = fields.Char(string='Memo')
    doc_payment_id = fields.Many2one('payment.doc', string=u'Numéro')
    cheque_objet = fields.Selection(related='doc_payment_id.objet', string='Objet de Chèque', readonly=1)
    cheque_type = fields.Selection(related='doc_payment_id.type', string='Type de Chèque', readonly=1)
    # objet = fields.Char('Motif de paiement')
    partner_reference = fields.Char(u'Référence client', readonly=1, states={'open': [('readonly', False)]})
    domiciliation = fields.Char(related='doc_payment_id.domiciliation', string='Domiciliation', readonly=1)
    ordonateur = fields.Char(related='doc_payment_id.ordonateur', string='Ordonateur', readonly=1)
    observation = fields.Char('Observation')
    state = fields.Selection([('1', 'operation'), ('2', u'Terminé')], default='1')

    def action_appliquer(self):
        # vérifier changement de montant
        if self.amount != self.amount_commercial:
            self.name.amount = self.amount
            self.name.observation = u'Le montant à payer a été rectifié de : ' + str(
                self.amount_commercial) + u' a : ' + str(self.amount) + u'(le montant payé)'
        payment_id = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'payment_method_id': 2,
            'mode_paiement_id': self.mode_paiement_id.id,
            'partner_type': 'customer',
            'partner_id': self.partner_id.id,
            'currency_id': self.currency_id.id,
            'amount': self.amount,
            'date': self.payment_date,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'echeance_id': self.echeance_id.id,
            'doc_payment_id': self.doc_payment_id.id,
            'writeoff_label': u'paiement échéance # de la commande #',
            'partner_reference': self.partner_reference,
            'cheque_objet': self.cheque_objet,
            'cheque_type': self.cheque_type,
            'dl_date': self.name.date,
            'observation': self.observation,
        })
        if self.journal_id.sequence_id :
            seq = self.journal_id.sequence_id
            move = payment_id.move_id
            payment_id.move_id.name = seq.with_context(ir_sequence_date=move.date).next_by_id()
        if self.echeance_id:
            self.echeance_id.date_paiement = payment_id.date
            self.echeance_id.montant_restant -= self.amount
            if self.echeance_id.montant_restant < 1:
                self.echeance_id.state = 'done'
            else:
                self.echeance_id.state = 'open'
        self.name.state = 'done'
        self.name.payment_id = payment_id.id
        if payment_id:
            payment_id.action_post()
            self.state = '2'
        return self.env.ref('crm_echeancier.act_report_recu_paiement').report_action(payment_id.id)
