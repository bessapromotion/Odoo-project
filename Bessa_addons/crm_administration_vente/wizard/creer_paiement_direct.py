# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError


class CreerPaiementChargeWizardDirect(models.TransientModel):
    _name = 'creer.paiement.charge.wizard.direct'
    _description = u'Créer le paiement des charges direct'

    charge_id = fields.Many2one('charge.annual', string=u'Référence Dossier Acquérreur',
                                default=lambda self: self.env.context['active_id'])
    currency_id = fields.Many2one(related='charge_id.currency_id')
    amount = fields.Monetary('Montant', currency_field='currency_id')
    company_id = fields.Many2one(related='charge_id.company_id', store=True)
    order_id = fields.Many2one(related='charge_id.order_id', string='Commande', readonly=True)
    num_dossier = fields.Char(related='charge_id.num_dossier', string=u'N° Dossier', readonly=True)
    product = fields.Many2one(related='charge_id.product', string='Appartement')
    partner_id = fields.Many2one('product.partner', string='Client',
                                 store=True, domain="[('product_id', '=', product)]", readonly=False, required=True)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])
    type_doc = fields.Selection(related='charge_id.type_doc', store=True)
    payment_date = fields.Date('Date', required=True, copy=False)
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement', required=True)
    communication = fields.Char(string='Memo')
    doc_payment_id = fields.Many2one('payment.doc', string=u'Numéro')
    cheque_objet = fields.Selection(related='doc_payment_id.objet', string='Objet de Chèque')
    cheque_type = fields.Selection(related='doc_payment_id.type', string='Type de Chèque')
    # objet = fields.Char('Motif de paiement')
    partner_reference = fields.Char(related='partner_id.name.ref', string=u'Référence client',
                                    states={'open': [('readonly', False)]})
    domiciliation = fields.Char(related='doc_payment_id.domiciliation', string='Domiciliation')
    ordonateur = fields.Char(related='doc_payment_id.ordonateur', string='Ordonateur')
    observation = fields.Char('Observation')
    state = fields.Selection([('1', 'operation'), ('2', u'Terminé')], default='1')
    type_paiement = fields.Selection([('year', 'Annuel'),
                                      ('month', u'Mensuel')], string='Type du paiement',
                                     tracking=True)
    duree = fields.Integer(u'Durée')
    year_ids = fields.Many2many('charge.year', string=u'Années', required=True,
                                states={'draft': [('readonly', False)]})
    month_ids = fields.Many2many('charge.month', string=u'Mois',
                                 states={'draft': [('readonly', False)]})
    remise = fields.Boolean(u'Paiement Remise des clés',default=False)
    # def get_num_payment(self):
    #     req = "Select max(id) as num from charge_payment where payment_type='inbound' and date_part('year', dl_date)=%s and type_paiement='charge';"
    #     # req = "Select max(name) as num from account_payment where payment_type='inbound' and date_part('year', create_date)=%s;"
    #     self._cr.execute(req, (self.payment_date.year,))
    #     res = self._cr.dictfetchall()
    #     num = res[0].get('num')
    #     if not num:
    #         num = 'CUST.IN/Charge/' + str(self.payment_date)[0:4] + '/0001'
    #     else:
    #         x = str(num)
    #         tmp = x[-4:]
    #         vtmp = int(tmp) + 1
    #         num = 'CUST.IN/' + str(self.payment_date)[0:4] + '/' + "{0:0>4}".format(str(vtmp))
    #     return num

    # @api.multi
    def action_appliquer(self):
        # verifier si la caisse de la journée existe
        rec = self.env['crm.caisse'].search(
            [('date_today', '=', self.payment_date), ('company_id', '=', self.charge_id.company_id.id)])
        if rec.exists():
            if self.year_ids:
               year_ids = []
               month_ids = []
               for year in self.year_ids:
                    year_ids.append(year.id)
               if self.month_ids:

                   for month in self.month_ids:
                       month_ids.append(month.id)
               print(year_ids, month_ids)
            print(self.charge_id.project_id.id, self.charge_id.order_id.id)
            # invoices = self.env['account.invoice'].browse(self.invoice_id.id)
            print()
            payment_id = self.env['account.payment'].create({
                'name': '/',
                'mode_paiement_id': self.mode_paiement_id.id,
                'partner_id': self.partner_id.name.id,
                'currency_id': self.currency_id.id,
                'amount': self.amount,
                'date': self.payment_date,
                'ref': self.communication,
                'journal_id': self.journal_id.id,
                'charge_id': self.charge_id.id,
                'doc_payment_id': self.doc_payment_id.id,
                'writeoff_label': u'paiement échéance # de la commande #',
                'partner_reference': self.partner_reference,
                'cheque_objet': self.cheque_objet,
                'cheque_type': self.cheque_type,
                'dl_date': self.payment_date,
                'observation': self.observation,
                'type': self.charge_id.type_doc,
                'duree': self.duree,
                'num_dossier_charge': self.num_dossier,
                'order_id_charge': self.order_id.id,
                'charge_ok': True,
                'type_paiement': self.type_paiement,
                'year_ids': [(6, 0, year_ids)],
                'month_ids': [(6, 0, month_ids)],
                'remise': self.remise,
                'company_id': self.company_id.id,

            })
            if payment_id:
                payment_id.action_post()
                # self.name.state = 'done'
                self.state = '2'

                # si versement en espece
                if self.mode_paiement_id.id == 2:
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
                    if self.charge_id.type_doc == 'charge':
                        nature_id = 27
                        libelle = 'Paiement des charges copropriété de ' + self.charge_id.project_id.name
                    if self.charge_id.type_doc == 'tag':
                        nature_id = 28
                        libelle = 'Paiement des tags de ' + self.charge_id.project_id.name
                    depense_id = self.env['crm.depense'].create({
                        'type_id': 1,
                        'project_id': self.charge_id.project_id.id,
                        'benificiaire': self.partner_id.name.name,
                        'partner_id': self.partner_id.name.id,
                        'type_ben_id': 3,
                        'nature_id': nature_id,
                        'currency_id': self.currency_id.id,
                        'mt_debit': self.amount,
                        'debit_ok': True,
                        'credit_ok': False,
                        'date': self.payment_date,
                        'libelle': libelle,
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
                # si versement cheque,virement, versement  creer recette bancaire
                if self.mode_paiement_id.id in (1, 3, 4):
                    print('chequuue')
                    req = "SELECT mt_cumulated_balance FROM operation_bancaire WHERE id = (SELECT max(id) FROM operation_bancaire where company_id = %s)"
                    self._cr.execute(req, (self.company_id.id,))
                    res = self._cr.dictfetchone()
                    if res:
                        cumulated_balance = res.get('mt_cumulated_balance')
                    else:
                        cumulated_balance = 0
                    if self.charge_id.type_doc == 'charge':
                        nature_id = 27
                        libelle = 'Paiement des charges copropriété de ' + self.charge_id.project_id.name
                    if self.charge_id.type_doc == 'tag':
                        nature_id = 28
                        libelle = 'Paiement des tags de ' + self.charge_id.project_id.name
                    print('balance cheque', cumulated_balance)
                    operation_id = self.env['operation.bancaire'].create({
                        'type_id': 1,
                        'project_id': self.charge_id.project_id.id,
                        'benificiaire': self.partner_id.name.name,
                        'partner_id': self.partner_id.name.id,
                        'type_ben_id': 3,
                        'nature_id': nature_id,
                        'currency_id': self.currency_id.id,
                        'mt_debit': self.amount,
                        'debit_ok': True,
                        'credit_ok': False,
                        'date': self.payment_date,
                        'libelle': libelle,
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

            return self.env.ref('crm_administration_vente.act_report_recu_paiement_charge').report_action(payment_id.id)

        else:
            # si caisse de la journée n'existe pas
            raise UserError(_(
                u'La caisse de cette journée n\'existe pas, Veuillez la creer Puis valider ce paiement '))
