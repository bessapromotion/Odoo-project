# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import date
from lxml import etree


class AutorisationLocation(models.Model):
    _name = 'autorisation.location'
    _description = u'Autorisation de location '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char('Numero', readonly=1)
    reservation_id = fields.Many2one('crm.reservation', string=u'Réservation', required=True,
                                     states={'draft': [('readonly', False)]},
                                     domain="[('company_id', '=', company_id)]")
    order_id = fields.Many2one(related='reservation_id.order_id', required=1, readonly=1,
                               string=u'Réference Bon de commande',
                               states={'draft': [('readonly', False)]}, domain="[('state', 'not in', ('cancel', "
                                                                               "'sent', 'draft'))]")
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
    partner_ids = fields.One2many(related='product.partner_ids', string=u'Propriétaires', readonly=1)
    acquereur_id = fields.Many2one('product.partner', string=u"Propriétaire Actuel",
                                   store=True, domain="[('product_id', '=', product)]",required=1)
    num_dossier = fields.Char(related='order_id.num_dossier', string=u'N° Dossier', store=True,
                              tracking=True)
    partner_id = fields.Many2one(related='reservation_id.partner_id', string='Réservataire Initial', readonly=1, store=True)
    phone = fields.Char(related='partner_id.phone', string=u'Téléphone', readonly=1, store=True)
    mobile = fields.Char(related='partner_id.mobile', string='Mobile', readonly=1, store=True)
    photo = fields.Binary(related='partner_id.image_1920', string='Photo', store=True)
    type_bien = fields.Char(related='order_id.type_bien', string="Type du bien", store=True)
    # product_ids = fields.One2many(related='reservation_id.product_ids', string='Appartement', readonly=1)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    charge_recouv_id = fields.Many2one(related='reservation_id.charge_recouv_id', string=u'Chargé; de recouvrement',
                                       store=True)
    observation = fields.Char(string="Observation")
    # ordre_ids = fields.One2many('ordre.paiement.charge', 'charge_id', string='Ordre de paiement',
    #                             readonly=True,
    #                             domain=[('state', '!=', 'cancel')], store=True)
    currency_id = fields.Many2one('res.currency', string='Devise', store=True)
    format_id = fields.Many2one(related='product_ids.format_id', string='Typologie')
    etage = fields.Many2one(related='product_ids.etage', string='Etage')
    bloc = fields.Char(related='product_ids.bloc', string='Bloc')
    commune_id = fields.Many2one(related='product.commune_id', string='Commune', )
    societe = fields.Char(string=u'societe')
    num_lot = fields.Char('N° Lot', related='product_ids.num_lot')
    superficie = fields.Float('Superficie', related='product_ids.superficie')
    # article_ids = fields.Many2many('cahier.charge.article', 'articles')
    locataire_id = fields.Many2one('res.partner',string=u'Locataire',required=1)
    date_naissance = fields.Date(related="locataire_id.birthday", string=u'Date de naissace du locataire',required=1)
    lieu_naissance = fields.Char(related="locataire_id.place_of_birth", string=u'Lieu de naissance',required=1)
    act_naissance = fields.Char(u'Numéro acte de naissance',required=1)
    pi_date = fields.Date(u'Délivrée le ',required=1)
    pi_par = fields.Char('Par',required=1)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('autorisation.location') or '/'

        return super(AutorisationLocation, self).create(vals)

    # @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le dossier est déjà validé !'))
        else:
            # self.product_ids.unlink()

            rec = super(AutorisationLocation, self).unlink()
            return rec

    # @api.one
    def action_cancel(self):
        self.state = 'cancel'

    # @api.one
    def action_validate(self):
        if self.reservation_id.decision_id:
            if self.reservation_id.decision_id.state != 'valid':
                raise UserError(_(u'decision d\'affectation  non validée !'))
            else:
                if self.reservation_id.remise_id:
                    if self.reservation_id.remise_id.state != 'valid':
                        raise UserError(_(u'remise des clés non validée !'))
                    else:
                        self.state = 'valid'
                        self.locataire_id.etat ='Locataire'
                        self.env['product.partner'].create({
                            'name': self.locataire_id.id,
                            'origin': self.name,
                            'product_id': self.product.id,
                            'type': u'Locataire',
                        })
                else:
                    raise UserError(_(u'remise des clés non créé!'))
        else:
            raise UserError(_(u'decision d\'affectation non créé !'))

    @api.onchange('reservation_id')
    def onchange_order(self):
        if self.reservation_id:
            self.partner_id = self.reservation_id.partner_id.id
            self.commercial_id = self.reservation_id.commercial_id.id
            self.project_id = self.reservation_id.project_id.id
            self.type_bien = self.order_id.type_bien
            # self.invoice_id     = self.order_id.invoice_ids.id
            self.num_dossier = self.order_id.num_dossier

    # @api.depends('company_id')
    # def abv_company(self):
    #     if self.company_id.id == 1:
    #         self.societe = 'BPI'
    #     if self.company_id.id == 2:
    #         self.societe = 'BTI'
    #     print(self.societe)

    def action_print(self):
        # print(self.company_id)
        # print(self.env.company)

        if self.company_id != self.env.company:
            raise UserError(_(u'Société invalide ! \n\n  Veuillez séléctionner la bonne société !'))
        else:
            self.ensure_one()
            return self.env.ref('crm_administration_vente.act_report_autorisation_location').report_action(self)

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
