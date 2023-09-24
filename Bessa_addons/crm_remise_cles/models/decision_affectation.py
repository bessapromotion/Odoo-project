# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import conversion
from odoo.exceptions import UserError
from datetime import date
from lxml import etree


class DecisionAffectation(models.Model):
    _name = 'decision.affectation'
    _description = u'Décision Affectation '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    @api.depends('amount_ttc')
    def _display_number_to_word(self):
        self.amount_lettre_ttc = conversion.conversion(self.amount_ttc)

    name = fields.Char('Numero', readonly=1)
    reservation_id = fields.Many2one('crm.reservation', string=u'Réservation', required=True,
                                     states={'draft': [('readonly', False)]})
    order_id = fields.Many2one(related='reservation_id.order_id', required=1, readonly=1,
                               string=u'Réference Bon de commande',
                               states={'draft': [('readonly', False)]}, domain="[('state', 'not in', ('cancel', "
                                                                               "'sent', 'draft'))]")
    mode_achat = fields.Selection(related='order_id.mode_achat', string='Mode Achat', readonly=1, store=True)
    partner_reservation_id = fields.Many2one(related='reservation_id.partner_id', required=1, readonly=1,
                                             string=u'Réservataire')
    invoice_id = fields.Many2one(related='order_id.invoice_id', readonly=1,
                                 string=u'Facture')
    amount_untaxed = fields.Monetary(related='invoice_id.amount_untaxed', string='Montant HT', store=True,
                                     readonly=True, tracking=True)
    amount_tva = fields.Monetary(string='Montant TVA', store=True, readonly=True, tracking=True,
                                 compute='calcul_tva_ttc')
    amount_ttc = fields.Monetary(string='Montant TTC', store=True, readonly=True, tracking=True,
                                 compute='calcul_tva_ttc')
    commercial_id = fields.Many2one(related='reservation_id.commercial_id', string='Commercial', readonly=1, store=True)
    project_id = fields.Many2one(related='reservation_id.project_id', string='Projet', readonly=1,
                                 states={'draft': [('readonly', False)]}, store=True)
    date = fields.Date('Date', required=1, default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', u'Validée'), ('cancel', 'Annulé')], string='Etat', default='draft',
                             tracking=True)
    product_ids = fields.One2many(related='reservation_id.product_ids', string='APPARTEMENT', readonly=1,
                                  states={'draft': [('readonly', False)]})
    product_name = fields.Char(related='product_ids.name.name', string='Nom de l\'Appartement')
    product = fields.Many2one(related='product_ids.name', string='Appartement')
    num_dossier = fields.Char(related='order_id.num_dossier', string=u'N° Dossier', store=True,
                              tracking=True)
    partner_id = fields.Many2one('product.partner', string='Client',
                                 store=True, domain="[('product_id', '=', product)]")
    type_bien = fields.Char(related='order_id.type_bien', string="Type du bien", store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    charge_recouv_id = fields.Many2one(related='reservation_id.charge_recouv_id', string=u'Chargé; de recouvrement',
                                       store=True)
    observation = fields.Char(string="Observation")
    currency_id = fields.Many2one('res.currency', string='Devise', store=True,
                                  default=lambda self: self.env.company.currency_id.id)
    format_id = fields.Many2one(related='product_ids.format_id', string='Typologie')
    etage = fields.Many2one(related='product_ids.etage', string='Etage')
    bloc = fields.Char(related='product_ids.bloc', string='Bloc')
    commune_id = fields.Many2one(related='product.commune_id', string='Commune', )
    societe = fields.Char(string=u'societe')
    num_lot = fields.Char('N° Lot', related='product_ids.num_lot')
    superficie = fields.Float('Superficie', related='product_ids.superficie')
    amount_lettre_ttc = fields.Char(compute=_display_number_to_word, string='Montant en lettres', readonly=1)
    signataire = fields.Boolean(u'Signataire', store=True, tracking=True)
    new_partner_id = fields.Many2one('res.partner', string='Nouveau Signataire', tracking=True, store=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('decision.affectation') or '/'

        return super(DecisionAffectation, self).create(vals)

    # @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le dossier est déjà validé !'))
        else:
            # self.product_ids.unlink()

            rec = super(DecisionAffectation, self).unlink()
            return rec

    # @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.depends('partner_id', 'order_id')
    def calcul_tva_ttc(self):
        echeance = self.env['crm.echeancier'].search(
            [('order_id', '=', self.order_id.id), ('type', '=', 'tva'),('partner_id', '=', self.partner_reservation_id.id),('state', '=', 'done')])
        print(echeance)
        self.amount_tva = echeance.montant_prevu
        print(echeance.montant_prevu)
        self.amount_ttc = self.amount_untaxed + self.amount_tva
        print(self.amount_tva)
        print(self.amount_ttc)

    def add_partner_id(self):
        if not self.product.partner_ids:
            print(self.partner_reservation_id.id)
            print(self.name)
            print(self.product.id)
            self.env['product.partner'].create({
                'name': self.partner_reservation_id.id,
                'origin': self.reservation_id.name,
                'product_id': self.product.id,
                'type':u'Réservataire',
            })

    def action_validate(self):
        echeance_notaire = self.env['crm.echeancier'].search(
            [('order_id', '=', self.order_id.id), ('type', '=', 'notaire'),
             ('partner_id', '=', self.partner_reservation_id.id),
             ('state', '=', 'done')])
        if echeance_notaire:
            if echeance_notaire.montant_prevu != echeance_notaire.montant:
                raise UserError(
                    _(u'Validation non autorisée ! \n\n  Les frais de notaire ne sont pas soldés veuillez vérifier !'))
            else:
                if not self.partner_id:
                    raise UserError(
                        _(u'il faut ajouter le reservataire à la table des propriétaires ! \n\n  En cliquant sur le bouton Ajouter Reservataire !'))

                self.state = 'valid'
                self.calcul_tva_ttc()
                if self.signataire:
                  self.new_partner_id.etat = 'signataire'
                  product_partner_id = self.env['product.partner'].create({
                    'name': self.new_partner_id.id,
                    'origin': self.name,
                    'product_id': self.product.id,
                    'type': u'Signataire',
                  })
                  print(product_partner_id)
                    #'type': u'Signataire',
                self.reservation_id.decision_id = self.id
        else:
            raise UserError(
                _(u'Validation non autorisée ! \n\n  Les frais de notaire ne sont pas soldés veuillez vérifier !'))

    @api.onchange('reservation_id', 'order_id')
    def onchange_order(self):
        if self.reservation_id:
            self.partner_id = self.reservation_id.partner_id.id
            self.commercial_id = self.reservation_id.commercial_id.id
            self.project_id = self.reservation_id.project_id.id
            self.type_bien = self.order_id.type_bien
            self.invoice_id = self.order_id.invoice_id.id
            self.num_dossier = self.order_id.num_dossier

    def action_print(self):
        self.ensure_one()
        if self.company_id.id != self.env.company.id:
            print(self.company_id.id)
            print(self.env.company.id)
            raise UserError(_(u'Société invalide ! \n\n  Veuillez séléctionner la bonne société !'))
        else:
            if self.mode_achat == '1':
               return self.env.ref('crm_remise_cles.act_decision_affectation_client').report_action(self)
            else:
                return self.env.ref('crm_remise_cles.act_decision_affectation_client_credit').report_action(self)

    #   Priviléges
    @api.model
    def fields_view_get(self, view_id=None, view_type=None, toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        group_receptionniste = self.env['res.users'].has_group('gestion_profil.group_commercial')
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
        if group_caissier or group_receptionniste or group_res_commercial or group_commercial or group_charg_recouvrement or group_res_recouvrement or group_assistante_adv or group_comptable_stock or group_res_compta:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('editable', 'none')
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

        if group_adv or group_res_adv:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '1')
                node.set('create', '1')
                node.set('edit', '1')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '1')
                node.set('editable', 'none')
                node.set('create', '1')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '1')
                node.set('create', '1')
                node.set('edit', '0')
                node.set('delete', '0')

        if group_commercial:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('editable', 'none')
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
