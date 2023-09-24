# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime as dt
from datetime import datetime

from datetime import date
from odoo.tools import conversion
from lxml import etree


class Depense(models.Model):
    _name = 'crm.depense'
    _description = u'Dépenses '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    @api.depends('mt_debit', 'mt_credit')
    def _display_number_to_word(self):
        for rec in self:
            rec.mt_debit_lettre = conversion.conversion(rec.mt_debit)
            rec.mt_credit_lettre = conversion.conversion(rec.mt_credit)



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
    credit_ok = fields.Boolean(u'Crédit', store=True, tracking=True, default=False)
    debit_ok = fields.Boolean(u'Débit', store=True, tracking=True, default=False)
    type_id = fields.Many2one('depense.type', string=u'Type', required=True,
                              states={'draft': [('readonly', False)]}, store=True)
    employee_id = fields.Many2one('hr.employee', string=u'Employé Bénificiaire',
                                  states={'draft': [('readonly', False)]}, tracking=True, store=True)
    department_id = fields.Many2one('hr.department', u'Département')
    benificiaire = fields.Char(string=u"Bénificiaire", required=True)
    compte_id = fields.Many2one('res.company.account', string='Compte',
                                states={'draft': [('readonly', False)]}, store=True, required=True, tracking=True)
    mt_debit = fields.Monetary(string=u'Montant Débit', store=True, tracking=True)
    mt_credit = fields.Monetary(string=u'Montant Crédit', store=True, tracking=True)
    tresorerie = fields.Selection([('banque', 'Banque'),
                                   ('caisse', u'Caisse')], string=u"Trésoreries", tracking=True, store=True,
                                  required=True, )
    tags_ids = fields.Many2many('depense.tag', string='Etiquette', store=True, readonly=1)
    type_ben_id = fields.Many2one('depense.type.benificaire', string=u'Type de bénificaire', store=True,
                                  states={'draft': [('readonly', False)]}, required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partenaire',
                                 states={'draft': [('readonly', False)]}, tracking=True, store=True)
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', u'Validée'), ('cancel', 'Annulé')], string='Etat', default='draft',
                             tracking=True)
    company_id = fields.Many2one('res.company', string=u'Société', default=lambda self: self.env.company)
    bloc = fields.Char(string="Bloc", store=True, tracking=True)
    periode = fields.Char(string=u'Période', store=True, tracking=True)
    observation = fields.Char(string="Observation", store=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string='Devise', store=True,
                                  default=lambda self: self.env.company.currency_id.id)
    mt_balance = fields.Monetary(string=u"Balance", store=True, tracking=True, readonly=1)
    mt_cumulated_balance = fields.Monetary(string=u"Balance Cumulée", store=True, tracking=True,
                                           readonly=1)
    mode_achat = fields.Selection([('1', 'Auto'), ('2', 'Crédit'), ('3', 'Mixte'), ], string='Mode Achat',
                                  store=True, tracking=True, readonly=1)
    origin = fields.Char(string="Document d'origine", store=True, tracking=True, required=True)
    mt_debit_lettre = fields.Char(compute=_display_number_to_word, string=u'Montant Débit en lettres', readonly=1)
    mt_credit_lettre = fields.Char(compute=_display_number_to_word, string='Montant Crédit en lettres', readonly=1)
    origin_fonds = fields.Char(string="ORIGINES DES FONDS", store=True, tracking=True)
    destination_fonds = fields.Char(string=u'DESTINATION DES FONDS', store=True, tracking=True)

    @api.model
    def create(self, vals):
        if vals['credit_ok']:
            vals['name'] = self.env['ir.sequence'].get('depense') or '/'
        if vals['debit_ok']:
            vals['name'] = self.env['ir.sequence'].get('recette') or '/'
        datee = dt.datetime.strptime(str(vals['date']), "%Y-%m-%d")
        date_today = dt.datetime.strptime(str(date.today()), "%Y-%m-%d")
        vals['month'] = datee.month
        vals['week'] = datee.isocalendar()[1]
        print(type(vals['date']))
        #if datee < date_today:
        #    raise UserError(
        #        _(u'Vous ne pouvez pas créer une fiche de dépense avec une date antérieure ! \n\n  Veuillez séléctionner une autre date !'))
        record = super(Depense, self).create(vals)

        return record

    # @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le dossier est déjà validé !'))
        else:
            # self.product_ids.unlink()

            rec = super(Depense, self).unlink()
            return rec

    # @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.onchange('mt_credit', 'mt_debit')
    def get_total_balance(self):
        for rec in self:

            rec.mt_balance = rec.mt_debit - rec.mt_credit
            req = "SELECT mt_cumulated_balance FROM crm_depense WHERE id = (SELECT max(id) FROM crm_depense)"
            self._cr.execute(req)
            res = self._cr.dictfetchall()
            print(res)
            if res:
                cumulated_balance = res[0].get('mt_cumulated_balance')
                if cumulated_balance:
                    print('rec.nature_id', rec.nature_id.id)
                    print('rec.type_ben_id', rec.type_ben_id.id)
                    if rec.nature_id.id != 1 and rec.type_ben_id.id != 3:

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
                date_today = dt.datetime.strptime(str(date.today()), "%Y-%m-%d")
                #if datee < date_today:
                #    raise UserError(
                #        _(u'Vous ne pouvez pas créer une fiche de dépense avec une date antérieure ! \n\n  Veuillez séléctionner une autre date !'))
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
        if self.type_ben_id.id == 1:
            print(self.employee_id.name)
            if not self.benificiaire:
               self.benificiaire = self.employee_id.name
               self.department_id = self.employee_id.department_id.id
        else:
            if not self.benificiaire:
               self.benificiaire = self.partner_id.name

    def create_mouvement(self):
        if self.nature_id.id == 26 and self.credit_ok == True:

            mouvement_id = self.env['crm.depense'].create({
                'type_id': self.type_id.id,
                'project_id': self.company_id.id,
                'benificiaire': self.benificiaire,
                'partner_id': self.partner_id.id,
                'employee_id': self.employee_id.id,
                'type_ben_id': self.type_ben_id.id,
                'nature_id': self.nature_id.id,
                'currency_id': self.currency_id.id,
                'mt_debit': self.mt_credit,
                'debit_ok': True,
                'credit_ok': False,
                'date': self.date,
                'department_id': self.department_id.id,
                'libelle': "Alimentation caisse Dépense",
                'caisse_id': self.caisse_id.id,
                'company_id': self.project_id.id,
                'origin': self.name,
                'tresorerie': 'caisse',
                'compte_id': 1,
                'origin_fonds': self.origin_fonds,
                'destination_fonds': self.destination_fonds,

            })

            if mouvement_id:
                mouvement_id.set_benificiaire()
                mouvement_id.set_tags()

            print("mouvement created")
            return mouvement_id


    def action_validate(self):
        if not self.credit_ok and not self.debit_ok:
           raise UserError(_(
                u'Veuillez Cocher crédit ou débit pour savoir s\'il s\'agit d\'une dépense ou recette !!!'))
        else:
           if self.date:
            rec = self.env['crm.caisse'].search(
                [('date_today', '=', self.date), ('company_id', '=', self.company_id.id)])
            if rec.exists():
                self.caisse_id = rec.id
                #self.get_total_balance()
                self.state = 'valid'
                self.set_tags()
                for tag in self.tags_ids:
                    print(tag.name)
                self.set_benificiaire()
                mouvement_id = self.create_mouvement()
                if mouvement_id:
                   mt_cumulated_balance = self.mt_cumulated_balance
                   mouvement_id.mt_balance = mouvement_id.mt_debit - mouvement_id.mt_credit
                   mouvement_id.mt_cumulated_balance = mt_cumulated_balance + mouvement_id.mt_balance
                   print("mouvement mt_cumulated_balance", mouvement_id.mt_cumulated_balance)
            else:
                raise UserError(_(
                    u'La caisse de cette journée n\'existe pas, Veuillez la creer Puis valider ce paiement '))

    def print_fiche_depense(self):

        return self.env.ref('crm_depenses.act_report_fiche_depense').report_action(self.id)

    def print_fiche_mouvement(self):

        return self.env.ref('crm_depenses.act_report_fiche_mouvement').report_action(self.id)

    def print_recu_paiement(self):
        if self.nature_id.id in (27,28,12):
            return self.env.ref('crm_depenses.act_report_recu_paiement').report_action(self.id)
        if self.nature_id.id == 41:
            return self.env.ref('crm_depenses.act_report_recu_paiement_classique').report_action(self.id)