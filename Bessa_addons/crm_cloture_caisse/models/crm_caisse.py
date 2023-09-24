# -*- coding: utf-8 -*-

from odoo import api
from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools import conversion
from lxml import etree
from datetime import datetime, date


class CrmCaisse(models.Model):
    _name = 'crm.caisse'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('open_ids')
    def _nbr_opens(self):
        for rec in self:
            rec.nbr_opens = len(rec.open_ids)

    @api.depends('mt_total_physique')
    def _display_number_to_word(self):
        for rec in self:
            rec.mt_total_physique_lettre = conversion.conversion(rec.mt_total_physique)
            rec.mt_coffre_depart_lettre = conversion.conversion(rec.mt_coffre_depart)

    name = fields.Char('Numero', readonly=1)
    date_today = fields.Date(string=u'Date de la journee', store=True, tracking=True)
    mt_total = fields.Monetary(string='Montant Total', store=True, compute='get_valeur_total_recette', tracking=True)
    mt_tva = fields.Monetary(string='Montant Total TVA', store=True, compute='get_valeur_total_recette', tracking=True)
    mt_notaire = fields.Monetary(string='Montant Total Notaire', store=True, compute='get_valeur_total_recette',
                                 tracking=True)
    payment_ids = fields.One2many('account.payment', 'caisse_id', string='Payments', readonly=1, store=True)
    state = fields.Selection(
        [('draft', 'Nouveau'), ('open', 'Ouverte'), ('valid', 'Validé'), ('done', 'Cloturée'), ('cancel', 'Annulé'), ],
        string='Status', default='draft', required=True, tracking=True)

    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.company_id.currency_id.id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    journal_id = fields.Many2one('account.journal', string='Payment Journal',
                                 domain=[('type', 'in', ('bank', 'cash'))])
    mt_liquidite = fields.Monetary(string='Montant Total Liquidite', store=True, compute='get_valeur_total_recette',
                                   tracking=True)
    mt_banque = fields.Monetary(string='Montant Total banque', store=True, compute='get_valeur_total_recette',
                                tracking=True)

    note = fields.Html('Observation')
    bill_ids = fields.One2many('caisse.bill', 'caisse_id', string='Pieces/Billets', store=True)
    mt_total_physique = fields.Monetary(string='Montant Total Physique', store=True, compute='get_total_physique',
                                        tracking=True)
    mt_total_physique_lettre = fields.Char(compute=_display_number_to_word, string='Montant en lettres', readonly=1)

    nombre_total_physique = fields.Integer(string='Nombre Total Piece', store=True, compute='get_total_physique',
                                           tracking=True)
    ecart = fields.Monetary(string='Ecart', store=True, compute='get_total_physique', tracking=True)
    currency = fields.Char(string="Devise", default="DA")
    mt_coffre_depart = fields.Monetary(string=u'Montant du coffre ouverture', store=True,
                                       tracking=True)
    mt_coffre_cloture = fields.Monetary(string='Montant du coffre cloture', store=True,
                                        tracking=True, readonly=1)
    mt_coffre_depart_lettre = fields.Char(compute=_display_number_to_word, string='Montant  en lettres', readonly=1)
    # bill_ids_coffre = fields.One2many('caisse.bill', 'caisse_id', string='Pieces/Billets', store=True)
    open_ids = fields.One2many('open.caisse.wizard', 'caisse_id', string='Ouverture caisse')
    nbr_opens = fields.Integer(compute=_nbr_opens, string='Ouvertures', readonly=0)
    observation = fields.Char(string="Observation")
    depense_ids = fields.One2many('crm.depense', 'caisse_id', string=u'Dépenses', readonly=1, store=True,
                                  domain="[('nature_id.id', '!=', 27)]")
    mt_total_depense = fields.Monetary(string='Différence', store=True, compute='get_valeur_total_depense',
                                       tracking=True)
    mt_debit = fields.Monetary(string='Montant Total Débit', store=True, compute='get_valeur_total_depense',
                               tracking=True)
    mt_credit = fields.Monetary(string='Montant Total Crédit', store=True, compute='get_valeur_total_depense',
                                tracking=True)
    solde_today = fields.Monetary(string='Solde de la journée', store=True,
                                  tracking=True, readonly=1)
    mt_total_transfert = fields.Monetary(string='Montant Total Transfert', store=True, compute='get_valeur_total_depense',
                               tracking=True)
    mt_total_alimentation_destination = fields.Monetary(string='Montant Total Alimentation a partir de société', store=True,
                                         compute='get_valeur_total_depense',
                                         tracking=True)
    mt_total_alimentation_company = fields.Monetary(string='Montant Total Alimentation meme-société', store=True,
                                            compute='get_valeur_total_depense',
                                            tracking=True)
    mt_cloture_depense = fields.Monetary(string='Montant cloture caisse depense', store=True,
                                                    compute='get_valeur_total_depense',
                                                    tracking=True)
    mt_alimentation_centrale = fields.Monetary(string='Montant alimentation caisse centrale', store=True,
                                         compute='get_valeur_total_depense',
                                         tracking=True)
    mt_total_alimentation_source = fields.Monetary(string='Montant Total Alimentation d\'autres sociétés',
                                                        store=True,
                                                        compute='get_valeur_total_depense',
                                                        tracking=True)

    @api.model
    def create(self, vals):
        rec = self.env['crm.caisse'].search(
            [('date_today', '=', self.date_today), ('company_id', '=', self.company_id.id)])
        if rec.exists():
            raise UserError(_(
                u'Une caisse de cette journée existe déjà, veuillez vérifier la date saisi ou la société choisi '))
        else:
            vals['name'] = "Caisse/" + str(vals['date_today'])
            record = super(CrmCaisse, self).create(vals)

        return record

    @api.depends('date_today')
    def get_valeur_total_recette(self):
        domain1 = []
        payments = []
        for rec in self:
            if rec.date_today:
                domain1 += [('dl_date', '=', rec.date_today),
                            ('company_id.id', '=', rec.company_id.id)]
                domain1 += [('move_id.state', '=', 'posted')]
                # if self.journal_id:
                #     domain1 += [('journal_id', '=', self.journal_id.name)]
                payments = self.env['account.payment'].search(domain1)
                rec.payment_ids = payments
                rec.mt_total = 0
                rec.mt_tva = 0
                rec.mt_notaire = 0
                rec.mt_liquidite = 0
                rec.mt_banque = 0
                rec.currency = "DA"
                for p in payments:
                    print(p.echeance_id.company_id.id)
                    print(p.dl_date)
                    rec.mt_total += p.amount
                    rec.currency_id = p.currency_id.id
                    if p.echeance_id.name == "#TVA":
                        rec.mt_tva += p.amount
                    if p.echeance_id.name == "#Notaire":
                        rec.mt_notaire += p.amount
                    if p.mode_paiement_id.id == 2:
                        rec.mt_liquidite += p.amount
                    else:
                        rec.mt_banque += p.amount

    @api.depends('date_today','state')
    def get_valeur_total_depense(self):
        domain2 = []
        depenses = []
        for rec in self:
            if rec.date_today:
                domain2 += [('date', '=', rec.date_today),
                            ('company_id.id', '=', rec.company_id.id)]
                domain2 += [('state', '=', 'valid'),
                            ('nature_id.id', '!=', 1)]
                depenses = self.env['crm.depense'].search(domain2)
                # print("Depenses", depenses)
                rec.depense_ids = depenses
                rec.mt_total_depense = 0
                rec.mt_debit = 0
                rec.mt_credit = 0
                rec.mt_total_transfert = 0
                rec.mt_total_alimentation_company = 0
                rec.mt_total_alimentation_destination = 0
                rec.mt_total_alimentation_source = 0
                rec.mt_cloture_depense = 0
                rec.mt_alimentation_centrale = 0
                rec.currency = "DA"
                for d in depenses:
                    if d.debit_ok:
                        if d.nature_id.id == 26:
                            if d.company_id.id == d.project_id.id:
                               rec.mt_debit += d.mt_debit
                               rec.mt_total_alimentation_company += d.mt_debit
                            else:
                               print(d.id)
                               print(rec.mt_total_alimentation_destination)

                               rec.mt_total_alimentation_destination += d.mt_debit
                        else:
                            if d.nature_id.id == 34:
                                rec.mt_cloture_depense += d.mt_debit
                            rec.mt_debit += d.mt_debit
                    if d.credit_ok:
                        if d.nature_id.id not in (26, 3, 36, 38):
                            rec.mt_credit += d.mt_credit
                        if d.nature_id.id == 26 and d.company_id.id != d.project_id.id:
                            rec.mt_total_alimentation_source += d.mt_credit
                        if d.nature_id.id == 3:
                            rec.mt_total_transfert += d.mt_credit
                        if d.nature_id.id == 36:
                            rec.mt_alimentation_centrale += d.mt_credit

                rec.mt_total_depense = rec.mt_debit - rec.mt_credit

    @api.depends('bill_ids')
    def get_total_physique(self):
        for rec in self:
            rec.mt_total_physique = 0
            rec.nombre_total_physique = 0
            rec.ecart = 0
            for bill in rec.bill_ids:
                rec.mt_total_physique += bill.montant
                rec.nombre_total_physique += bill.nombre
            rec.ecart = rec.mt_total_physique - rec.mt_liquidite - rec.mt_debit + rec.mt_credit
            rec.solde_today = rec.mt_liquidite + rec.mt_debit - rec.mt_credit

    def action_calculer(self):
        self.state = 'open'
        self.get_valeur_total_recette()
        self.get_valeur_total_depense()

    def action_validate(self):
        self.state = 'valid'
        self.get_total_physique()


    def action_cancel(self):
        self.state = 'cancel'

    def action_reopen(self):
        self.state = 'draft'

    def action_cloturer(self):
         #if self.ecart > 5000 and not self.observation:
        #    raise UserError(_(
        #        u'L\'écart de la journée est supérieur au seuil, Vous devez renseigner le motif dans le champ observation ensuite cloturer la caisse !'))
        self.state = 'done'
        self.mt_coffre_cloture = self.mt_coffre_depart + self.mt_liquidite + self.mt_debit - self.mt_credit - self.mt_total_transfert + self.mt_total_alimentation_destination - self.mt_total_alimentation_company - self.mt_cloture_depense - self.mt_alimentation_centrale - self.mt_total_alimentation_source

    @api.depends('date_today')
    def get_all_payment_today(self):
        domain1 = []
        if self.date_today:
            domain1 += [('dl_date', '=', self.date_today),
                        ('company_id.id', '=', self.company_id.id)]
            domain1 += [('move_id.state', '=', 'posted')]
            # if self.journal_id:
            #     domain1 += [('journal_id', '=', self.journal_id.name)]
        payments = self.env['account.payment'].search(domain1)
        return payments

    def print_payment_report(self):
        payments = self.get_all_payment_today()
        print(self.mt_total, "tVA", self.mt_tva, "Notaire", self.mt_notaire)
        payment_list = []
        for p in payments:
            vals = {
                'num_dossier': p.num_dossier,
                'client': p.partner_id.name,
                'Montant': p.amount,
                'projet': p.project_id.name,
                'commercial': p.commercial_id.name,
                'Motif_paiement': p.ref,
                'mode_paiement': p.mode_paiement_id.name,
                'type_paiement': p.motif_paiement,
                'journal': p.journal_id.name,
            }
            payment_list.append(vals)
        data = {
            'form_data': self.read()[0],
            'payments': payment_list
        }
        # print(data)
        return self.env.ref('crm_cloture_caisse.action_report_cloture_caisse_xml').report_action(self, data=data)

    def print_pv_caisse(self):
        bill_list = []
        bills = self.bill_ids
        for bill in bills:
            vals = {
                'bill': bill.bill_id.name,
                'nombre': bill.nombre,
                'montant': bill.montant,
            }
            bill_list.append(vals)
        print(self.bill_ids)
        data = {
            'form_data': self.read()[0],
            'billets': bill_list
        }
        # print(data)
        return self.env.ref('crm_cloture_caisse.action_report_pv_caisse_xml').report_action(self)

    @api.model
    def fields_view_get(self, view_id=None, view_type=None, toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        group_commercial = self.env['res.users'].has_group('gestion_profil.group_commercial')
        group_res_commercial = self.env['res.users'].has_group('gestion_profil.group_res_commercial')
        group_charg_recouvrement = self.env['res.users'].has_group('gestion_profil.group_charg_recouvrement')
        group_res_recouvrement = self.env['res.users'].has_group('gestion_profil.group_res_recouvrement')
        group_adv = self.env['res.users'].has_group('gestion_profil.group_adv')
        group_res_adv = self.env['res.users'].has_group('gestion_profil.group_res_adv')
        group_assistante_adv = self.env['res.users'].has_group('gestion_profil.group_assistante_adv')
        group_comptable_stock = self.env['res.users'].has_group('gestion_profil.group_comptable_stock')
        group_res_compta = self.env['res.users'].has_group('gestion_profil.group_res_compta')
        group_caissier = self.env['res.users'].has_group('gestion_profil.group_caissier')

        doc = etree.XML(res['arch'])
        # consu
        if group_caissier or group_comptable_stock or group_res_compta:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '1')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)

        return res
