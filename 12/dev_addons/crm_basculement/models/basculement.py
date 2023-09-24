# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from odoo.tools import conversion
# import datetime
from dateutil import relativedelta


class CrmBasculement(models.Model):
    _name = 'crm.basculement'
    _description = 'Basculement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    @api.depends('affectation_ids')
    def _total_new_affecation(self):
        for rec in self:
            rec.b_price_2 = sum(line.price_2 for line in rec.affectation_ids)
            rec.b_montant_lettre = conversion.conversion(rec.b_price_2)

    @api.depends('a_price_2', 'b_price_2', 'total_paiement')
    def _paiements(self):
        for rec in self:
            rec.reste_paiement = rec.a_price_2 - rec.total_paiement
            reste = rec.b_price_2 - rec.total_paiement
            if reste > 0:
                rec.b_reste_paiement = reste
                rec.b_a_rembourser = 0.0
            else:
                rec.b_reste_paiement = 0.0
                rec.b_a_rembourser = -1 * reste

    @api.one
    @api.depends('prix_vente')
    def _a_montant_lettre(self):
        for rec in self:
            rec.a_montant_lettre = conversion.conversion(rec.prix_vente)

    name = fields.Char('Numero', readonly=1)
    commercial_id = fields.Many2one('res.users', required=1, string='Commercial', readonly=1,
                                    states={'draft': [('readonly', False)]})
    charge_recouv_id = fields.Many2one('res.users', required=1, string='Chargé de Recouvrement', readonly=1,
                                       states={'draft': [('readonly', False)]})
    date = fields.Date('Date', required=1, default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    motif = fields.Text('Motif', readonly=1, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Nouveau'),
                              ('done', 'Validée'),
                              ('cancel', 'Annulée'), ], string='Etat', default='draft', track_visibility='onchange')
    reservation_id = fields.Many2one('crm.reservation', string='Réservation', required=True, readonly=1,
                                     states={'draft': [('readonly', False)]})
    product_ids = fields.Many2one('crm.reservation.product', string='Bien(s)')
    partner_id = fields.Many2one(related='reservation_id.partner_id', string='Client', readonly=1, store=True)
    phone = fields.Char(related='partner_id.phone', string='Téléphone', readonly=1)
    mobile = fields.Char(related='partner_id.mobile', string='Mobile', readonly=1)
    photo = fields.Binary(related='partner_id.image', string='Photo')
    date_reservation = fields.Date(related='reservation_id.date', string=u'Date réservation', readonly=1, store=True)
    # A
    #     a_project_id   = fields.Many2one(related='reservation_id.project_id', string='Projet', readonly=1, store=True)
    a_product_id = fields.Many2one('product.template', string='Bien affecté')
    # a_bloc         = fields.Char(related='a_product_id.bloc', string='Bloc', readonly=1)
    # a_type_id      = fields.Many2one(related='a_product_id.type_id', string='Type du bien', readonly=1)
    # a_format_id    = fields.Many2one(related='a_product_id.format_id', string='Type', readonly=1)
    # a_orientation  = fields.Many2one(related='a_product_id.orientation', string='Orientation', readonly=1)
    # a_etage        = fields.Many2one(related='a_product_id.etage', string='Etage', readonly=1)
    # a_superficie   = fields.Float(related='a_product_id.superficie', string='Superficie', readonly=1)
    # a_prix_m2      = fields.Float(related='a_product_id.prix_m2', string='Prix m2', readonly=1)
    a_price_2 = fields.Float(related='a_product_id.price_2', string='Prix vente', readonly=1)
    # B
    #     b_project_id   = fields.Many2one('project.project', string='Nouveau Projet', required=1, store=True)
    #     b_product_id   = fields.Many2one('product.template', string='Nouvelle affectation', required=1, store=True)
    #     b_bloc         = fields.Char(related='b_product_id.bloc', string='Bloc', readonly=1)
    #     b_type_id      = fields.Many2one(related='b_product_id.type_id', string='Nouveau type du bien', readonly=1)
    #     b_format_id    = fields.Many2one(related='b_product_id.format_id', string='Type', readonly=1)
    #     b_orientation  = fields.Many2one(related='b_product_id.orientation', string='Orientation', readonly=1)
    #     b_etage        = fields.Many2one(related='b_product_id.etage', string='Etage', readonly=1)
    #     b_superficie   = fields.Float(related='b_product_id.superficie', string='Superficie', readonly=1)
    #     b_prix_m2      = fields.Float(related='b_product_id.prix_m2', string='Prix m2', readonly=1)
    b_price_2 = fields.Float(compute=_total_new_affecation, string='Prix vente', readonly=1)
    b_order_id = fields.Many2one('sale.order', string='Nouvelle commande', readonly=True)
    b_reservation_id = fields.Many2one('crm.reservation', string='Nouvelle réservation', readonly=True)

    # info
    order_id = fields.Many2one(related='reservation_id.order_id', string='Commande')
    prix_vente = fields.Monetary(related='order_id.amount_untaxed', string='Prix de vente (HT)')
    a_montant_lettre = fields.Char(compute=_a_montant_lettre, string='Montant en lettre')
    total_paiement = fields.Monetary(string='Montant versé', readonly=1, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(related='reservation_id.order_id.currency_id', string='Devise')
    reste_paiement = fields.Monetary(compute=_paiements, string='Reste a payer')

    b_reste_paiement = fields.Monetary(compute=_paiements, string=u'Montant à payer')
    b_a_rembourser = fields.Monetary(compute=_paiements, string=u'Montant à rembourser')
    b_montant_lettre = fields.Char(compute=_total_new_affecation, string='Montant en lettre')
    b_num_dossier = fields.Char(u'Numéro nouveau dossier', readonly=1, states={'draft': [('readonly', False)]})
    bien_ids = fields.One2many(related='reservation_id.product_ids', readonly=1)
    affectation_ids = fields.One2many('crm.basculement.affectation', 'basculement_id', string='Nouvelle affectation',
                                      readonly=1, states={'draft': [('readonly', False)]})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('crm.basculement') or '/'

        return super(CrmBasculement, self).create(vals)

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Suppression non autorisée ! \n\n  Le basculement est déjà validée !'))
        else:
            # self.product_ids.unlink()

            rec = super(CrmBasculement, self).unlink()
            return rec

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    def create_order(self):
        # mise a jour fiche article
        try:
            order = self.env['sale.order'].create({
                'origin': self.name,
                'charge_recouv_id': self.charge_recouv_id.id,
                'pricelist_id': 1,
                'state': 'draft',
                'date_order': self.date,
                'validity_date': self.date,
                'confirmation_date': self.date,
                'user_id': self.commercial_id.id,
                'partner_id': self.partner_id.id,
                'company_id': self.env.user.company_id.id,
                'team_id': 1,
                'payment_term_id': 1,
                # 'opportunity_id': ,
                'project_id': self.affectation_ids[0].project_id.id,
                'num_dossier': self.b_num_dossier,
                'create_auto': True,
            })
        except:
            raise UserError(_('erreur creation devis !'))

        # lines = []
        for rec in self.affectation_ids:
            try:
                prod = self.env['product.product'].search([('product_tmpl_id', '=', rec.name.id)])[0].id
                self.env['sale.order.line'].create({
                    # lines.append({
                    'order_id': order.id,
                    'name': rec.name.name,
                    'sequance': 10,
                    'prix_m2': rec.prix_m2,
                    'price_unit': rec.price_2,
                    'price_subtotal': rec.price_2,
                    'price_tax': 0.0,
                    'price_total': rec.price_2,
                    'product_id': prod,
                    'product_uom_qty': 1.0,
                    'product_uom': 1,
                    'salesman_id': self.commercial_id.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'company_id': self.env.user.company_id.id,
                    'order_partner_id': self.partner_id.id,
                    'state': 'draft',
                })
            except:
                raise UserError(_('erreur ligne devis !'))

        # order.order_line = lines

        # confirmer le devis
        order.action_confirm()
        return order.id

    def create_reservation(self):
        reservation = self.env['crm.reservation'].create({
            'order_id': self.b_order_id.id,
            'partner_id': self.partner_id.id,
            # 'invoice_id': invoice.id,
            'date': self.date,
            'date_limite': self.date,
            'commercial_id': self.commercial_id.id,
            'charge_recouv_id': self.charge_recouv_id.id,
            'basculement_src_id': self.reservation_id.id,
        })

        reservation.onchange_devis()
        reservation.state = 'valid'
        reservation.partner_id.etat = 'Réservataire'
        for rec in reservation.product_ids:
            rec.name.client_id = self.partner_id.id
            rec.name.etat = 'Réservé'
            rec.name.order_id = self.b_order_id.id
            rec.name.reservation_id = reservation.id
            # annuler tous les autres devis
            for dvs in rec.name.line_ids:
                if dvs.order_id.name != self.b_order_id.name:
                    dvs.order_id.action_cancel()
                    dvs.order_id.motif_annulation = 'Prereservation'

        return reservation.id

    def create_remboursement(self, amount):
        self.env['crm.remboursement'].create({
            'commercial_id': self.commercial_id.id,
            'charge_rembours_id': self.charge_recouv_id.id,
            'date': date.today(),
            'motif': 'Remboursement généré suite a un basculement #' + self.name,
            'state': 'open',
            'reservation_id': self.b_reservation_id.id,
            'montant_a_rembourser': amount,
            'montant_rembourse': 0.0,
            'montant_restant': amount,
        })

    def create_echeance(self, amount, e_date):
        self.env['crm.echeancier'].create({
            'name': '#Basculement',
            'order_id': self.b_order_id.id,
            'label': 'Tranche complémentaire suite au bascuelement #' + self.name,
            'date_creation': date.today(),
            'date_prevue': e_date,
            'montant_prevu': amount,
            'type': 'tranche',
            'montant': 0.0,
        })

    @api.one
    def action_validate(self):
        # mettre la réservation sous l'état 'basculée'
        for rec in self.affectation_ids:
            if rec.name and rec.prix_m2 <= 0:
                raise UserError(_(u'Le prix du bien doit être supérier à 0.'))
            else:
                pass
        self.reservation_id.state = 'bascul'

        # annuler le bon de commande original
        self.order_id.action_cancel()
        self.order_id.motif_annulation = 'Basculement'

        # liberer les bien
        for rec in self.bien_ids:
            rec.name.client_id = None
            rec.name.order_id = None
            rec.name.reservation_id = None
            rec.name.etat = 'Libre'

        # créer les nouveaux documents
        # 1 - commande
        self.b_order_id = self.create_order()
        # 2 - réservation
        self.reservation_id.basculement_dst_id = self.create_reservation()
        self.b_reservation_id = self.reservation_id.basculement_dst_id.id
        # 3 - paiement
        # meme prix -> transferer les echeances
        if self.prix_vente == self.b_price_2:
            for rec in self.order_id.echeancier_ids:
                rec.order_id = self.b_order_id.id
        else:
            total_echeance = 0
            last_ech_date = date.today()
            ech_lst = self.env['crm.echeancier'].search([('order_id', '=', self.order_id.id), ('state', '=', 'done')])
            for rec in ech_lst:
                total_echeance += rec.montant
                rec.order_id = self.b_order_id.id
                last_ech_date = rec.date_prevue
            # remboursement
            if total_echeance > self.b_price_2:
                # annuler le reste des echeances
                ech_lst_cancel = self.env['crm.echeancier'].search([('order_id', '=', self.order_id.id), ('state', '!=', 'done')])
                for rec in ech_lst_cancel:
                    rec.order_id = self.b_order_id.id
                    rec.state = 'cancel'
                # créer le remboursement
                self.create_remboursement(total_echeance - self.b_price_2)
            # create_echeance
            if total_echeance < self.b_price_2:
                ech_lst_reste = self.env['crm.echeancier'].search([('order_id', '=', self.order_id.id), ('state', '!=', 'done')])
                ok = True
                for rec in ech_lst_reste:
                    rec.order_id = self.b_order_id.id
                    if ok:
                        if rec.state != 'cancel':
                            if total_echeance + rec.montant_prevu <= self.b_price_2:
                                total_echeance += rec.montant_prevu
                                last_ech_date = rec.date_prevue
                            else:
                                montant_derniere_echeance = self.b_price_2 - total_echeance
                                rec.montant_prevu = montant_derniere_echeance
                                ok = False
                                rec.state='cancel'
                    else:
                        rec.state = 'cancel'

                if total_echeance < self.b_price_2:
                    # créer une nouvelle echeance avec la difference de prix
                    # dt = last_ech_date
                    last_ech_date = last_ech_date + relativedelta.relativedelta(months=1)
                    # mois = dt.month + 1
                    # an = 0
                    # if mois > 12:
                    #     mois = mois - 12
                    #     an = 1
                    # dt = dt.replace(year=dt.year + an)
                    # last_ech_date = dt.replace(month=mois)  # Modifier par RABIE le 10/03/2021
                    # last_ech_date = last_ech_date.month + datetime.timedelta(days=diff)
                    self.create_echeance(self.b_price_2 - total_echeance, last_ech_date)

        self.state = 'done'

    @api.onchange('reservation_id')
    def onchange_reservation(self):
        if self.reservation_id:
            self.commercial_id = self.reservation_id.commercial_id.id
            self.charge_recouv_id = self.reservation_id.charge_recouv_id.id
            self.total_paiement = self.reservation_id.total_paiement
            if len(self.reservation_id.product_ids) >= 1:
                self.product_ids = self.reservation_id.product_ids[0]
                self.a_product_id = self.reservation_id.product_ids[0].name.id
        else:
            self.commercial_id = None
            self.charge_recouv_id = None
            self.product_ids = None
            self.a_product_id = None

    # @api.onchange('product_ids')
    # def onchange_product_ids(self):
    #     if self.product_ids:
    #         self.a_product_id = self.product_ids.name
    #     else:
    #         self.a_project_id = None
    #         self.a_bloc = None
    #         self.a_etage = None
    #         self.a_format_id = None
    #         self.a_orientation = None
    #         self.a_superficie = None
    #         self.a_prix_m2 = None
    #         self.a_price_2 = None

    def action_open_new_reservation(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.reservation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.b_reservation_id.id,
            'target': 'current',
        }

    def action_open_new_order(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.b_order_id.id,
            'target': 'current',
        }

    @api.multi
    def action_print(self):
        return self.env.ref('crm_basculement.act_report_basculement').with_context(
            {'discard_logo_check': True}).report_action(self)


class CrmBasculementAffectation(models.Model):
    _name = 'crm.basculement.affectation'
    _description = 'Basculement Nouvelle affectation'

    @api.depends('prix_m2')
    def _calcul_price_2(self):
        self.price_2 = self.prix_m2 * self.superficie

    project_id = fields.Many2one('project.project', string='Projet')
    name = fields.Many2one('product.template', string='Appartement', required=True,domain="[('project_id', '=', project_id)]")
    bloc = fields.Char(related='name.bloc', string='Bloc', readonly=1)
    type_id = fields.Many2one(related='name.type_id', string='Type du bien', readonly=1)
    format_id = fields.Many2one(related='name.format_id', string='Type', readonly=1)
    orientation = fields.Many2one(related='name.orientation', string='Orientation', readonly=1)
    etage = fields.Many2one(related='name.etage', string='Etage', readonly=1)
    superficie = fields.Float(related='name.superficie', string='Superficie', readonly=1)
    num_lot = fields.Char(related='name.num_lot', string='N° Lot', readonly=1)
    prix_m2 = fields.Float(string='Prix_m2', readonly=0)
    price_2 = fields.Float(string='Prix de vente', compute='_calcul_price_2')
    note = fields.Char('Notes')
    a_product_id = fields.Many2one(related='basculement_id.a_product_id')
    basculement_id = fields.Many2one('crm.basculement', String='Basculement')

    # partner_id       = fields.Many2one(related='basculement_id.partner_id', string='Client', readonly=1)
    # commercial_id    = fields.Many2one(related='basculement_id.commercial_id', string='Commercial', readonly=1)
    # charge_recouv_id = fields.Many2one(related='basculement_id.charge_recouv_id', string='Chargé de recouvrement', readonly=1)

    @api.onchange('project_id')
    def onchange_project(self):
        self.name = None

    @api.multi
    @api.onchange('name')
    def price_unit_change(self):
        if self.name:
            self.prix_m2 = self.name.prix_m2
