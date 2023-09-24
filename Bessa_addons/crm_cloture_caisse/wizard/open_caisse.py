# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from odoo.exceptions import UserError
from odoo.tools import conversion
from lxml import etree

from datetime import datetime
from dateutil.relativedelta import relativedelta


class OpenCaisseWizard(models.Model):
    _name = 'open.caisse.wizard'
    _description = u'Ouverture de caisse'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('mt_coffre_lettre')
    def _display_number_to_word(self):
        for rec in self:
            rec.mt_coffre_lettre = conversion.conversion(rec.mt_coffre)
            rec.mt_coffre_physique_lettre = conversion.conversion(rec.mt_coffre_physique)

    name = fields.Char('Numero', readonly=1)
    date_today = fields.Date(u'Date',default=lambda self: fields.Date.today(), required=True)
    date_yesterday = fields.Date(u'Date Décompte', compute='get_decompte_date')
    journal_id = fields.Many2one('account.journal', string='Payment Journal',
                                 domain=[('type', 'in', ('bank', 'cash'))])
    mt_coffre = fields.Monetary(string='Montant du coffre', store=True,
                                tracking=True, digits='Product Price')
    mt_coffre_lettre = fields.Char(compute=_display_number_to_word, string='Montant en lettres', readonly=1)
    mt_coffre_cloture = fields.Monetary(string='Montant du coffre de cloture', store=True,
                                        tracking=True, readonly=1, compute='get_coffre_cloture', digits='Product Price')
    currency_id = fields.Many2one('res.currency', string='Devise', store=True,
                                  default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    bill_ids_coffre = fields.One2many('caisse.bill', 'open_caisse_id', string='Pieces/Billets', store=True)
    mt_coffre_physique = fields.Monetary(string='Montant du coffre calculé', store=True,
                                         compute='get_mt_coffre_physique', readonly=1,
                                         tracking=True, digits='Product Price')
    mt_coffre_physique_lettre = fields.Char(compute=_display_number_to_word, string='Montant  en lettres', readonly=1)
    caisse_id = fields.Many2one('crm.caisse', string='Caisse', store=True)
    currency = fields.Char(string="Devise", default="DA")
    versement = fields.Boolean(string="Versement")
    mt_versement = fields.Monetary(string='Montant de versement', store=True, tracking=True, digits='Product Price')
    observation = fields.Char(string="Observation")
    ecart = fields.Monetary(string='Ecart', store=True,
                            tracking=True, readonly=1, compute='get_mt_coffre_physique', digits='Product Price')
    state = fields.Selection(
        [('draft', 'Brouillon'), ('done', 'Validée')], string='Status', default='draft', required=True, tracking=True)

    # @api.model
    # def create(self, vals):
    #     vals['name'] = "Ouverture/caisse/" + str(self.date_today)
    #     record = super(OpenCaisseWizard, self).create(vals)

    @api.depends('date_today')
    def get_decompte_date(self):
        for rec in self:
            if rec.date_today:
                rec.date_yesterday = rec.date_today - relativedelta(days=1)

    @api.depends('bill_ids_coffre')
    def get_mt_coffre_physique(self):
        for rec in self:
            rec.mt_coffre_physique = 0
            for bill in rec.bill_ids_coffre:
                rec.mt_coffre_physique += bill.montant
            rec.ecart = rec.mt_coffre_physique - rec.mt_coffre

    @api.depends('date_today', 'company_id')
    def get_coffre_cloture(self):
        if self.date_today:
            self.date_yesterday = self.date_today - relativedelta(days=1)
            rec = self.env['crm.caisse'].search(
                [('date_today', '=', fields.Date.to_string(self.date_today - relativedelta(days=1))),
                 ('company_id', '=', self.company_id.id)])
            self.mt_coffre_cloture = rec.mt_coffre_cloture

    def action_open(self):
        if self.company_id.id == 1:
            self.name = 'Ouverture_Caisse_BPI/' + str(self.date_today)
        if self.company_id.id == 2:
            self.name = 'Ouverture_Caisse_BTI/' + str(self.date_today)
        if self.company_id.id == 3:
            self.name = 'Ouverture_Caisse_BBA/' + str(self.date_today)
        if self.company_id.id == 4:
            self.name = 'Ouverture_Caisse_BMA/' + str(self.date_today)
        if self.company_id.id == 5:
            self.name = 'Ouverture_Caisse_SIMONTO/' + str(self.date_today)
        if self.company_id.id == 6:
            self.name = 'Ouverture_Caisse_BLA/' + str(self.date_today)
        if self.company_id.id == 7:
            self.name = 'Ouverture_Caisse_BTS/' + str(self.date_today)
        # vérifier changement de montant
        if self.date_today and self.company_id:
            self.state = 'done'
            self.get_mt_coffre_physique()
            for bill in self.bill_ids_coffre:
                bill.state = 'open'
            rec = self.env['crm.caisse'].search(
                [('date_today', '=', self.date_today), ('company_id', '=', self.company_id.id)])
            if rec.exists():
                raise UserError(_(
                    u'Une caisse de cette journée existe déjà, veuillez vérifier la date saisi ou la société choisi '))
            else:
                if not self.mt_coffre:
                    self.mt_coffre = self.mt_coffre_physique
                if self.versement and self.mt_coffre_cloture:
                    self.mt_coffre = self.mt_coffre_cloture - self.mt_versement
                caisse = self.env['crm.caisse'].create({
                    'date_today': self.date_today,
                    'company_id': self.company_id.id,
                    'mt_coffre_depart': self.mt_coffre,
                    'currency_id': self.currency_id.id,
                    'name': 'Caisse/' + str(self.date_today),

                })
                if caisse:
                    self.caisse_id = caisse.id
                    caisse.get_valeur_total_recette()
                    caisse.get_valeur_total_depense()
                    report_ref = self.env.ref('crm_cloture_caisse.action_report_pv_coffre_xml').report_action(self)
                    report_ref['close_on_report_download'] = True

                    return report_ref

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
