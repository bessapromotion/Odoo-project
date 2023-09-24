# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime as dt
from datetime import datetime

from datetime import date
from lxml import etree


class OperationBancaire(models.Model):
    _name = 'operation.bancaire'
    _description = u'Opérations Bancaires '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char('Numero', readonly=1, store=True)
    date = fields.Date('Date', required=1, default=lambda self: fields.Date.today(), states={'draft': [('readonly', False)]}, store=True,
                       tracking=True)
    month = fields.Integer(string=u'Mois', required=True, readonly=1, store=True)
    week = fields.Integer(string=u'Semaine', required=True, readonly=1, store=True)
    project_id = fields.Many2one('depense.project', string=u'Projet', required=True,
                                 states={'draft': [('readonly', False)]}, store=True)
    libelle = fields.Char(string=u"Libelle", store=True, required=True, tracking=True)
    nature_id = fields.Many2one('depense.nature', string=u'Nature', required=True,
                                states={'draft': [('readonly', False)]}, store=True)
    credit_ok = fields.Boolean(u'Crédit', store=True, tracking=True)
    debit_ok = fields.Boolean(u'Débit', store=True, tracking=True)
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement')
    doc_payment_id = fields.Many2one('payment.doc', string=u'Numéro')
    objet = fields.Char('Motif de paiement')
    cheque_num = fields.Char(u'Numéro')
    cheque_domiciliation = fields.Char('Domiciliation')
    cheque_ordonateur = fields.Char('Ordonnateur')
    cheque_date = fields.Date(u'Date chèque')
    observation = fields.Char('Observation')
    cheque_objet = fields.Selection([('normalise', 'NORMALISE'), ('avance', 'AVANCE')], string='Objet de Chèque')
    cheque_type = fields.Selection(
        [('no_certifie', 'NON CERTIFIE'), ('certifie', 'CERTIFIE'), ('credit', 'CHEQUE CREDIT')],
        string='Type de Chèque')
    type_id = fields.Many2one('depense.type', string=u'Type', required=True,
                              states={'draft': [('readonly', False)]}, store=True)
    employee_id = fields.Many2one('hr.employee', string=u'Employé Bénificiaire',
                                  states={'draft': [('readonly', False)]}, tracking=True, store=True)
    benificiaire = fields.Char(string=u"Bénificiaire", required=True)
    compte_id = fields.Many2one('res.company.account', string='Compte',
                                states={'draft': [('readonly', False)]}, store=True, tracking=True)
    mt_debit = fields.Monetary(string=u'Montant Débit', store=True, tracking=True, default=False)
    mt_credit = fields.Monetary(string=u'Montant Crédit', store=True, tracking=True, default=False)
    tresorerie = fields.Selection([('banque', 'Banque'),
                                   ('caisse', u'Caisse')], string=u"Trésoreries", tracking=True, store=True,
                                  required=True, default='banque')
    tags_ids = fields.Many2many('depense.tag', string='Etiquette', store=True, readonly=1)
    type_ben_id = fields.Many2one('depense.type.benificaire', string=u'Type de bénificaire', store=True,
                                  states={'draft': [('readonly', False)]}, required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partenaire',
                                 states={'draft': [('readonly', False)]}, tracking=True, store=True)
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', u'Validée'), ('cancel', 'Rejetée')], string='Etat', default='draft',
                             tracking=True)
    company_id = fields.Many2one('res.company', string=u'Société', default=lambda self: self.env.company, readonly=1)

    observation = fields.Char(string="Observation", store=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise', store=True,
                                  default=lambda self: self.env.company.currency_id.id)
    mt_balance = fields.Monetary(string=u"Balance", store=True, tracking=True, readonly=1)
    mt_cumulated_balance = fields.Monetary(string=u"Balance Cumulée", store=True, tracking=True,
                                           readonly=1)
    mode_achat = fields.Selection([('1', 'Auto'), ('2', 'Crédit'), ('3', 'Mixte'), ], string='Mode Achat',
                                  store=True, tracking=True, readonly=1)
    origin = fields.Char(string="Document d'origine", store=True, tracking=True, required=True)
    num_dossier = fields.Char('N° Dossier', store=True, tracking=True, readonly=1)

    @api.model
    def create(self, vals):
        if vals['credit_ok']:
            vals['name'] = self.env['ir.sequence'].get('depense_bancaire') or '/'
        if vals['debit_ok']:
            vals['name'] = self.env['ir.sequence'].get('recette_bancaire') or '/'
        datee = dt.datetime.strptime(str(vals['date']), "%Y-%m-%d")
        vals['month'] = datee.month
        # my_datetime = datetime.combine(date, datetime.min.time())
        vals['week'] = datee.isocalendar()[1]
        # vals['mt_balance'] = vals['mt_debit'] - vals['mt_credit']
        # vals['mt_cumulated_balance'] = vals['mt_balance']
        
        if vals['cheque_num'] and vals['mode_paiement_id']:
            doc = self.env['payment.doc'].create({
            'name': vals['cheque_num'],
            'mode_paiement_id': vals['mode_paiement_id'],
            'domiciliation': vals['cheque_domiciliation'],
            'ordonateur': vals['cheque_ordonateur'],
            'date': vals['cheque_date'],
            'objet': vals['cheque_objet'],
            'type': vals['cheque_type'],
            })
            
            vals['doc_payment_id'] = doc.id        
        record = super(OperationBancaire, self).create(vals)

        return record

    # @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le dossier est déjà validé !'))
        else:
            # self.product_ids.unlink()

            rec = super(OperationBancaire, self).unlink()
            return rec

    # @api.one
    def action_cancel(self):
        self.state = 'cancel'


    @api.onchange('company_id', 'compte_id')
    def set_ordonnateur_domiciliation(self):
        if self.company_id and self.credit_ok:
            self.cheque_ordonateur = self.company_id.name
        if self.compte_id:
            self.cheque_domiciliation = self.compte_id.bank


    @api.onchange('mt_credit', 'mt_debit')
    def get_total_balance(self):
        for rec in self:

            rec.mt_balance = rec.mt_debit - rec.mt_credit
            req = "SELECT mt_cumulated_balance FROM operation_bancaire WHERE id = (SELECT max(id) FROM operation_bancaire where company_id = %s)"
            self._cr.execute(req, (self.company_id.id,))
            res = self._cr.dictfetchall()
            if res:
                cumulated_balance = res[0].get('mt_cumulated_balance')
                if cumulated_balance:
                    print('rec.nature_id', rec.nature_id.id)
                    print('rec.type_ben_id', rec.type_ben_id.id)
                    if rec.nature_id.id != 27 and rec.type_ben_id.id != 3:

                        print('cumulated balance', cumulated_balance)
                        rec.mt_cumulated_balance = rec.mt_balance + cumulated_balance
                    else:
                        print('cumulated balance', cumulated_balance)
                        print('non exectué')
                else:
                    print('cumulated balance', cumulated_balance)
                    rec.mt_cumulated_balance = rec.mt_balance

    @api.onchange('date')
    def get_month_week(self):
        for rec in self:
            if self.date:
                datee = dt.datetime.strptime(str(self.date), "%Y-%m-%d")
                rec.month = datee.month
                # my_datetime = datetime.combine(date, datetime.min.time())
                rec.week = datee.isocalendar()[1]

    @api.onchange('credit_ok', 'debit_ok')
    def set_tags(self):
        ids = []
        if self.credit_ok:
            ids = [1]
        if self.debit_ok:
            ids = [2]
        if self.credit_ok and self.debit_ok:
            ids = [1, 2]

        self.tags_ids = [(6, 0, ids)]
        self.write({'tags_ids': [(6, 0, ids)]})

    @api.onchange('employee_id', 'partner_id')
    def set_benificiaire(self):
        if self.type_ben_id == 1:
            if not self.benificiaire:
                self.benificiaire = self.employee_id.name
        else:
            if not self.benificiaire:
                self.benificiaire = self.partner_id.name

    # @api.one
    def action_validate(self):
          if self.date:
            #rec = self.env['crm.caisse'].search(
            #   [('date_today', '=', self.date), ('company_id', '=', self.company_id.id)])
            #if rec.exists():
            #    self.caisse_id = rec.id
                #self.get_total_balance()
            self.state = 'valid'
            self.set_tags()
            self.set_ordonnateur_domiciliation()
            for tag in self.tags_ids:
                    print(tag.name)
            self.set_benificiaire()
            #else:
            #    raise UserError(_(
            #        u'La caisse de cette journ�e n\'existe pas, Veuillez la creer Puis valider ce paiement '))

    def print_fiche_operation(self):

        return self.env.ref('crm_depenses.act_report_fiche_operation_bancaire').report_action(self.id)
