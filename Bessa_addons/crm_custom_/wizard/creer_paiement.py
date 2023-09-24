# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.exceptions import UserError


class CreerPaiementWizard(models.TransientModel):
    _inherit = 'creer.paiement.wizard'
    _name = 'creer.paiement.wizard'

    def action_appliquer(self):
        # vérifier changement de montant
        if self.amount != self.amount_commercial:
            self.name.amount = self.amount
            self.name.observation = u'Le montant à payer a été rectifié de : ' + str(
                self.amount_commercial) + u' a : ' + str(self.amount) + u'(le montant payé)'
        # rec = self.env['crm.caisse'].search(
        #     [('date_today', '=', self.payment_date), ('company_id', '=', self.echeance_id.company_id.id)])
        # print(rec.id)
        # if rec.exists():
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
                #'caisse_id': rec.id,
                'journal_id': self.journal_id.id,
                'echeance_id': self.echeance_id.id,
                'doc_payment_id': self.doc_payment_id.id,
                'writeoff_label': u'paiement échéance # de la commande #',
                'partner_reference': self.partner_reference,
                'cheque_objet': self.cheque_objet,
                'cheque_type': self.cheque_type,
                'dl_date': self.payment_date,
                'observation': self.observation,
                'charge_ok': False,
                'type': 'versement',
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
        if payment_id:
                payment_id.action_post()
                self.state = '2'
        return self.env.ref('crm_echeancier.act_report_recu_paiement').report_action(payment_id.id)

        # else:
        #     raise UserError(_(
        #         u'La caisse de cette journ�e n\'existe pas, Veuillez la creer Puis valider ce paiement '))
