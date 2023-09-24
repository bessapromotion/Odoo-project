# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class CreerPaiementOutWizard(models.TransientModel):
    _name = 'creer.paiement.out.wizard'

    name = fields.Many2one('crm.remboursement', string='Remboursement', required=1, readonly=1,
                           default=lambda self: self.env.context['active_id'])
    currency_id = fields.Many2one(related='name.currency_id')
    amount = fields.Monetary('Montant', currency_field='currency_id')
    reste = fields.Monetary(related='name.montant_restant', string='Reste à payer')
    partner_id = fields.Many2one(related='name.partner_id', string='Client', readonly=True)

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])

    payment_date = fields.Date('Date', required=True, copy=False)
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement', required=True)
    communication = fields.Char(string='Memo')
    doc_payment_id = fields.Many2one('payment.doc', string=u'Numéro')
    state = fields.Selection([('1', 'operation'), ('2', u'Terminé')], default='1')

    def get_num_payment(self):
        req = "Select max(name) as num from account_payment where payment_type='outbound' and date_part('year', create_date)=%s;"
        self._cr.execute(req, (datetime.now().year,))
        res = self._cr.dictfetchall()
        num = res[0].get('num')
        if not num:
            num = 'CUST.OUT/' + str(datetime.now())[0:4] + '/0001'
        else:
            tmp = num[-4:]
            vtmp = int(tmp) + 1
            num = 'CUST.OUT/' + str(datetime.now())[0:4] + '/' + "{0:0>4}".format(str(vtmp))
        return num

    # @api.multi
    def action_appliquer(self):
        if self.amount <= self.name.montant_restant:
            # invoices = self.env['account.invoice'].browse(self.invoice_id.id)
            payment_id = self.env['account.payment'].create({
                # 'invoice_ids'   : [(6, 0, invoices.ids)],
                'payment_type': 'outbound',
                'payment_method_id': 2,
                'mode_paiement_id': self.mode_paiement_id.id,
                'partner_type': 'customer',
                'partner_id': self.partner_id.id,
                'amount': self.amount,
                'currency_id': self.currency_id.id,
                'date': self.payment_date,
                'dl_date': self.payment_date,
                'observation': self.communication,
                'journal_id': self.journal_id.id,
                'remboursement_id': self.name.id,
                'est_remboursement': True,
                'doc_payment_id': self.doc_payment_id.id,
                'writeoff_label': 'Remboursement #' + self.name.name,
            })

            if payment_id:
                payment_id.action_post()
                if self.name.montant_restant <= 0.0:
                    self.name.state = 'done'
                # self.state = '2'

            # return self.env.ref('account.action_report_payment_receipt').report_action(payment_id.id)
            # return self.env.ref('crm_echeancier.act_report_recu_paiement').report_action(payment_id.id)
        else:
            raise UserError(_(
                'Le montant payé dépasse le reste a rembourser ! \n\n  Veuillez reverifier les informations du paiement !'))
