# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import conversion
from datetime import date


# import datetime


class CrmBasculement(models.Model):
    _name = 'crm.basculement'
    _inherit = 'crm.basculement'


    @api.depends('affectation_ids')
    def _total_new_affecation(self):
        for rec in self:
            rec.b_price_2 = sum(line.price_2 for line in rec.affectation_ids)
            rec.b_montant_lettre = conversion.conversion(rec.b_price_2)
        self.b_montant_lettre_total_order =   conversion.conversion(self.b_order_id.amount_total)

    name = fields.Char('Numero', readonly=1)
    commercial_id = fields.Many2one('res.users', required=1, string='Commercial', readonly=1,
                                    states={'draft': [('readonly', False)]})
    charge_recouv_id = fields.Many2one('res.users', required=1, string='Chargé de Recouvrement', readonly=1,
                                       states={'draft': [('readonly', False)]})
    date = fields.Date('Date', required=1, default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    motif = fields.Text('Motif', readonly=1, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Nouveau'),
                              ('done', 'Validée'),
                              ('cancel', 'Annulée'), ], string='Etat', default='draft', tracking=True)
    a_project_id = fields.Many2one(related='reservation_id.project_id', string='Ancien Projet', readonly=1, store=True)
    b_project_id = fields.Many2one(related='b_reservation_id.project_id', string='Nouveau Projet', required=1,
                                   store=True)
    b_product_id = fields.Many2one(related='affectation_ids.name', string='Nouvelle affectation', required=1,
                                   store=True)
    num_dossier = fields.Char(related='order_id.num_dossier', string=u'Num Dossier')
    mode_achat = fields.Selection(related='order_id.mode_achat', string=u'Mode Achat')
    reservation_id = fields.Many2one('crm.reservation', string='Réservation', required=True, readonly=1,
                                     states={'draft': [('readonly', False)]})
    product_ids = fields.Many2one('crm.reservation.product', string='Bien(s)')
    partner_id = fields.Many2one(related='reservation_id.partner_id', string='Client', readonly=1, store=True)
    phone = fields.Char(related='partner_id.phone', string='Téléphone', readonly=1)
    mobile = fields.Char(related='partner_id.mobile', string='Mobile', readonly=1)
    photo = fields.Binary(related='partner_id.image_1920', string='Photo')
    date_reservation = fields.Date(related='reservation_id.date', string=u'Date réservation', readonly=1, store=True)

    a_product_id = fields.Many2one('product.template', string='Bien affecté')

    a_price_2 = fields.Float(related='a_product_id.price_2', string='Prix vente', readonly=1)
    b_order_id = fields.Many2one('sale.order', string='Nouvelle commande', readonly=True)
    b_reservation_id = fields.Many2one('crm.reservation', string='Nouvelle réservation', readonly=True)

    # info
    order_id = fields.Many2one(related='reservation_id.order_id', string='Commande', store=True)
    prix_vente = fields.Monetary(related='order_id.amount_untaxed', string='Prix de vente (HT)')
    total_paiement = fields.Monetary(string='Montant versé', readonly=1, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(related='reservation_id.order_id.currency_id', string='Devise')

    b_num_dossier = fields.Char(u'Numéro nouveau dossier', readonly=1, states={'draft': [('readonly', False)]})
    bien_ids = fields.One2many(related='reservation_id.product_ids', readonly=1)
    affectation_ids = fields.One2many('crm.basculement.affectation', 'basculement_id', string='Nouvelle affectation',
                                      readonly=1, states={'draft': [('readonly', False)]})
    b_montant_lettre = fields.Char(compute=_total_new_affecation, string='Montant en lettre')
    b_montant_lettre_total_order =fields.Char(compute=_total_new_affecation, string='Montant en lettre')
    company_id = fields.Many2one('res.company', u'Société', related='reservation_id.project_id.company_id', store=True)

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
        if reservation.partner_id.etat != 'Acquéreur':
            reservation.partner_id.etat = 'Réservataire'
        for rec in reservation.product_ids:
            rec.name.client_id = self.partner_id.id
            rec.name.etat = 'Réservé'
            rec.name.order_id = self.b_order_id.id
            rec.name.reservation_id = reservation.id
            product_partner_id = self.env['product.partner'].create({
                'name': self.partner_id.id,
                'origin': self.name,
                'product_id': rec.name.id,
                'type': u'Réservataire aprés Basculement'
            })
            # annuler tous les autres devis
            for dvs in rec.name.line_ids:
                if dvs.order_id.name != self.b_order_id.name:
                    dvs.order_id.action_cancel()
                    dvs.order_id.motif_annulation = 'Prereservation'

        return reservation.id

    # Correction de la societe de l'ordre lors de la validation d'un basculement

    def create_order(self):
        # mise a jour fiche article
        # try:
        order = self.env['sale.order'].create({
            'origin': self.name,
            'charge_recouv_id': self.charge_recouv_id.id,
            'pricelist_id': 1,
            'state': 'draft',
            'date_order': self.date,
            'validity_date': self.date,
            # 'confirmation_date': self.date,
            'user_id': self.commercial_id.id,
            'partner_id': self.partner_id.id,
            'company_id': self.env.company.id,
            'team_id': 1,
            'payment_term_id': self.env.ref('account.account_payment_term_end_following_month').id,
            # 'opportunity_id': ,
            'project_id': self.affectation_ids[0].project_id.id,
            'num_dossier': self.b_num_dossier,
            'mode_achat':self.mode_achat,
            'create_auto': True,
        })
        # except:
        #     raise UserError(_('erreur creation devis !'))

        # lines = []
        for rec in self.affectation_ids:
            # try:
            prod = self.env['product.product'].search([('product_tmpl_id', '=', rec.name.id)])[0].id
            self.env['sale.order.line'].create({
                # lines.append({
                'order_id': order.id,
                'name': rec.name.name,
                'sequence': 10,
                'prix_m2': rec.prix_m2,
                'price_unit': rec.price_2,
                'price_subtotal': rec.price_2,
                'price_tax': 0.0,
                'price_total': rec.price_2,
                'product_id': prod,
                'product_uom_qty': 1.0,
                'product_uom': 1,
                'salesman_id': self.commercial_id.id,
                'currency_id': self.env.company.currency_id.id,
                'company_id': order.company_id.id,
                'order_partner_id': self.partner_id.id,
                'state': 'draft',
            })
            # except:
            #     raise UserError(_('erreur ligne devis !'))

        # order.order_line = lines

        # confirmer le devis
        order.action_confirm()
        return order.id

    def action_validate(self):
        # mettre la réservation sous l'état 'basculée'
        for rec in self.affectation_ids:
            if rec.name and rec.prix_m2 <= 0:
                raise UserError(_(u'Le prix du bien doit être supérieur à 0.'))
            else:
                pass
        self.reservation_id.state = 'bascul'

        # annuler le bon de commande original
        self.order_id.action_cancel()
        self.order_id.motif_annulation = 'Basculement'

        # liberer les bien
        for rec in self.bien_ids:
            # supprimer le client de la table des proprietaires
            self.env["product.partner"].search([('name', '=', rec.name.client_id.id),
             ('product_id', '=', rec.name.id)]).unlink()

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
            total_echeance = self.order_id.total_paiement2
            # remboursement
            if total_echeance > self.b_price_2:
                # annuler le reste des echeances
                ech_lst_cancel = self.env['crm.echeancier'].search(
                    [('order_id', '=', self.order_id.id), ('state', '!=', 'done')])
                for rec in ech_lst_cancel:
                    rec.order_id = self.b_order_id.id
                    rec.state = 'cancel'
                # créer le remboursement
                self.create_remboursement(total_echeance - self.b_price_2)

            # create_echeance
            if total_echeance < self.b_price_2:
                reste_paiement_echeance = self.b_reste_paiement - self.reste_paiement
                cumul_paiment = 0
                last_ech_date = fields.Date.today()
                for rec in self.order_id.echeancier_ids:
                    if rec.state != 'cancel':
                        taux = rec.montant_prevu / rec.amount_total_signed
                        mtn_echeance = taux * reste_paiement_echeance
                        if rec.state == 'done':
                            cumul_paiment += mtn_echeance
                        else:
                            rec.montant_prevu += cumul_paiment + mtn_echeance
                            cumul_paiment = 0

                        rec.order_id = self.b_order_id.id
                        last_ech_date = rec.date_prevue

                if cumul_paiment != 0:
                    self.create_echeance(cumul_paiment, last_ech_date + relativedelta.relativedelta(months=1))

        self.state = 'done'
