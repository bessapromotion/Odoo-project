# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class CreerPaiementWizard(models.TransientModel):
    _name = 'creer.paiement.wizard'

    name        = fields.Many2one('ordre.paiement', string='Ordre de paiement', required=1, readonly=1, default=lambda self: self.env.context['active_id'])
    order_id = fields.Many2one(related='name.order_id', string='Commande', readonly=True)
    invoice_id = fields.Many2one(related='name.invoice_id', string='Facture', readonly=True)
    partner_id = fields.Many2one(related='name.partner_id', string='Fournisseur', readonly=True)
    currency_id = fields.Many2one(related='name.currency_id')
    amount      = fields.Monetary(related='name.amount', string='Montant', currency_field='currency_id')
    objet      = fields.Char(related='name.objet', string='Objet')

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])

    payment_date = fields.Date('Date', required=True, copy=False)
    mode_paiement_id = fields.Many2one('payment.mode', string='Mode de paiement', required=True)
    communication = fields.Char(string='Memo')
    # doc_payment_id = fields.Many2one('payment.doc', string=u'Numéro')
    state = fields.Selection([('1', 'operation'), ('2', u'Terminé')], default='1')

    def get_num_payment(self):
        # req = "Select max(name) as num from account_payment where payment_type='inbound' and date_part('year', create_date)=%s;"
        # self._cr.execute(req, (datetime.now().year,))
        # res = self._cr.dictfetchall()
        # num = res[0].get('num')
        # if not num:
        #     num = 'CUST.IN/'+str(datetime.now())[0:4] + '/0001'
        # else:
        #     tmp = num[-4:]
        #     vtmp = int(tmp) + 1
        #     num = 'CUST.IN/'+str(datetime.now())[0:4] + '/' + "{0:0>4}".format(str(vtmp))
        # return num
        return self.env['ir.sequence'].get('account.payment.supplier.invoice') or '/'

    # @api.multi
    def action_appliquer(self):
        invoices = self.env['account.move'].browse(self.invoice_id.id)
        payment_id = self.env['account.payment'].create({
            'name'          : self.get_num_payment(),
            'invoice_ids'   : [(6, 0, invoices.ids)],
            'payment_type'  : 'outbound',
            'payment_method_id': 2,
            'mode_paiement_id' : self.mode_paiement_id.id,
            'partner_type'  : 'supplier',
            'partner_id'    : self.partner_id.id,
            'amount'        : self.amount,
            'currency_id'   : self.currency_id.id,
            'payment_date'  : self.payment_date,
            'communication' : self.communication,
            'journal_id'    : self.journal_id.id,
            # 'doc_payment_id': self.doc_payment_id.id,
            'ordre_paiement_id': self.name.id,
            'writeoff_label': self.objet,
        })

        if payment_id:
            payment_id.post()
            self.name.state = 'done'
            self.state = '2'

        # return self.env.ref('crm_echeancier.act_report_recu_paiement').report_action(payment_id.id)
