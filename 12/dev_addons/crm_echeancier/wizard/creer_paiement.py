# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class CreerPaiementWizard(models.TransientModel):
    _name = 'creer.paiement.wizard'

    name        = fields.Many2one('ordre.paiement', string='Ordre de paiement', required=1, readonly=1, default=lambda self: self.env.context['active_id'])
    echeance_id = fields.Many2one(related='name.echeance_id', string='Echeance')
    currency_id = fields.Many2one(related='name.currency_id')
    amount      = fields.Monetary('Montant', currency_field='currency_id')
    order_id  = fields.Many2one(related='name.order_id', string='Commande', readonly=True)
    partner_id  = fields.Many2one(related='name.partner_id', string='Client', readonly=True)

    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])

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

    def get_num_payment(self):
        req = "Select max(name) as num from account_payment where payment_type='inbound' and date_part('year', create_date)=%s;"
        self._cr.execute(req, (datetime.now().year,))
        res = self._cr.dictfetchall()
        num = res[0].get('num')
        if not num:
            num = 'CUST.IN/'+str(datetime.now())[0:4] + '/0001'
        else:
            tmp = num[-4:]
            vtmp = int(tmp) + 1
            num = 'CUST.IN/'+str(datetime.now())[0:4] + '/' + "{0:0>4}".format(str(vtmp))
        return num

    @api.multi
    def action_appliquer(self):
        # invoices = self.env['account.invoice'].browse(self.invoice_id.id)
        payment_id = self.env['account.payment'].create({
            'name'          : self.get_num_payment(),
            # 'invoice_ids'   : [(6, 0, invoices.ids)],
            'payment_type'      : 'inbound',
            'payment_method_id' : 2,
            'mode_paiement_id'  : self.mode_paiement_id.id,
            'partner_type'      : 'customer',
            'partner_id'        : self.partner_id.id,
            'amount'            : self.amount,
            'currency_id'       : self.currency_id.id,
            'payment_date'      : self.payment_date,
            'communication'     : self.communication,
            'journal_id'        : self.journal_id.id,
            'echeance_id'       : self.echeance_id.id,
            'doc_payment_id'    : self.doc_payment_id.id,
            'writeoff_label'    : 'paiement echeance # de la commande #',
            'partner_reference' : self.partner_reference,
            'cheque_objet'      : self.cheque_objet,
            'cheque_type'       : self.cheque_type,
            # 'objet'             : self.objet,
            'observation'       : self.observation,

        })

        if self.echeance_id:
            self.echeance_id.date_paiement = payment_id.payment_date
            # self.echeance_id.montant_restant -= self.amount
            if self.echeance_id.montant_restant == 0:
                self.echeance_id.state = 'done'
            else:
                self.echeance_id.state = 'open'

        if payment_id:
            payment_id.post()
            self.name.state = 'done'
            self.state = '2'

        # return self.env.ref('account.action_report_payment_receipt').report_action(payment_id.id)
        return self.env.ref('crm_echeancier.act_report_recu_paiement').report_action(payment_id.id)
