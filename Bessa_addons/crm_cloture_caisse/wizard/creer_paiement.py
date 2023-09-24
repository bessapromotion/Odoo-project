# -*- coding: utf-8 -*-
from odoo import models, _, fields, api
from odoo.exceptions import UserError


class CreerPaiementWizard(models.TransientModel):
    _inherit = 'creer.paiement.wizard'


    # add transfert value in type
    type = fields.Selection([('charge', 'Charge'),
                             ('tag', u'Tag'), ('versement', u'Versement'), ('transfert', 'Transfert de fond')],
                            string='Type du paiement', store=True,
                            tracking=True, default='versement')

    # asing type based on observation field
    @api.depends('observation')
    def set_type(self):
        if self.observation:
            index = self.observation.find('fond')
            if index != -1:
                self.type = 'transfert'
            else:
                self.type = 'versement'

    def action_appliquer(self):
        # vérifier changement de montant
        if self.amount != self.amount_commercial:
            self.name.amount = self.amount
            self.name.observation = u'Le montant à payer a été rectifié de : ' + str(
                self.amount_commercial) + u' a : ' + str(self.amount) + u'(le montant payé)'

        # verifier si la caisse de la journée existe
        rec = self.env['crm.caisse'].search(
            [('date_today', '=', self.payment_date), ('company_id', '=', self.echeance_id.company_id.id)])
        if rec.exists():
            # create payment
            self.set_type()
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
                'caisse_id': rec.id,
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
                'type': self.type,
		'company_id': self.company_id.id,

            })

            if self.journal_id.sequence_id:
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
                # si versement en espece  et ce n'est pas un transfert de fond creer recette
                if self.mode_paiement_id.id == 2 and self.type != 'transfert':
                    req = "SELECT mt_cumulated_balance FROM crm_depense WHERE id = (SELECT max(id) FROM crm_depense)"
                    self._cr.execute(req)
                    res = self._cr.dictfetchone()
                    if res:
                        cumulated_balance = res.get('mt_cumulated_balance')
                    else:
                        cumulated_balance = 0
                    print('balance paiement', cumulated_balance)
                    if self.company_id.id == 1:
                        compte_id = 1
                    if self.company_id.id == 2:
                        compte_id = 21
                    depense_id = self.env['crm.depense'].create({
                        'type_id': 1,
                        'project_id': self.echeance_id.project_id.id,
                        'benificiaire': self.partner_id.name,
                        'partner_id': self.partner_id.id,
                        'type_ben_id': 3,
                        'nature_id': 1,
                        'currency_id': self.currency_id.id,
                        'mt_debit': self.amount,
                        'debit_ok': True,
                        'credit_ok': False,
                        'date': self.payment_date,
                        'libelle': self.communication + ' de la commande ' + self.order_id.name + ' , N° Dossier ' + self.order_id.num_dossier,
                        'caisse_id': rec.id,
                        'company_id': self.company_id.id,
                        'mt_cumulated_balance': cumulated_balance + self.amount,
                        'mode_achat': self.order_id.mode_achat,
                        'origin': payment_id.move_id.name,
                        'tresorerie': 'caisse',
                        'compte_id': compte_id,

                    })
                    if depense_id:
                        depense_id.get_total_balance()
                        depense_id.action_validate()
                # si versement cheque,virement, versemnt  et ce n'est pas un transfert de fond creer recette bancaire
                if self.mode_paiement_id.id in (1, 3, 4) and self.type != 'transfert':
                    print('chequuue')
                    req = "SELECT mt_cumulated_balance FROM operation_bancaire WHERE id = (SELECT max(id) FROM operation_bancaire where company_id = %s)"
                    self._cr.execute(req, (self.company_id.id,))
                    res = self._cr.dictfetchone()
                    if res:
                        cumulated_balance = res.get('mt_cumulated_balance')
                    else:
                        cumulated_balance = 0

                    print('balance cheque', cumulated_balance)
                    operation_id = self.env['operation.bancaire'].create({
                        'type_id': 1,
                        'project_id': self.echeance_id.project_id.id,
                        'benificiaire': self.partner_id.name,
                        'partner_id': self.partner_id.id,
                        'type_ben_id': 3,
                        'nature_id': 1,
                        'currency_id': self.currency_id.id,
                        'mt_debit': self.amount,
                        'debit_ok': True,
                        'credit_ok': False,
                        'date': self.payment_date,
                        'libelle': self.communication + ' de la commande ' + self.order_id.name + ' , N° Dossier ' + self.order_id.num_dossier,
                        'caisse_id': rec.id,
                        'company_id': self.company_id.id,
                        'mt_cumulated_balance': cumulated_balance + self.amount,
                        'mode_achat': self.order_id.mode_achat,
                        'origin': payment_id.move_id.name,
                        'tresorerie': 'banque',
                        'mode_paiement_id': self.mode_paiement_id.id,
                        'doc_payment_id': self.doc_payment_id.id,
                        'cheque_num': self.doc_payment_id.name or ' ',
                        'cheque_domiciliation': self.doc_payment_id.domiciliation,
                        'cheque_ordonateur': self.doc_payment_id.ordonateur,
                        'cheque_date': self.doc_payment_id.date,
                        'cheque_objet': self.cheque_objet,
                        'cheque_type': self.cheque_type,
                        'tags_ids': [(6, 0, [2])]

                    })
                    if operation_id:
                        operation_id.get_total_balance()
                        operation_id.set_tags()

            return self.env.ref('crm_echeancier.act_report_recu_paiement').report_action(payment_id.id)

        else:
            # si caisse de la journée n'existe pas 
            raise UserError(_(
                u'La caisse de cette journée n\'existe pas, Veuillez la creer Puis valider ce paiement '))
