# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError
from datetime import datetime, date

class CrmReservation(models.Model):
    _name = 'crm.reservation'
    _inherit = 'crm.reservation'

    commercial_id = fields.Many2one(related='order_id.user_id', required=1, string='Commercial', readonly=1,
                                    states={'draft': [('readonly', False)]}, store=True, tracking=True)
    charge_recouv_id = fields.Many2one(related='order_id.charge_recouv_id', required=1, string='Chargé de Recouvrement',
                                       readonly=1,
                                       states={'draft': [('readonly', False)]}, store=True, tracking=True)
    order_id = fields.Many2one('sale.order', string='Associer un devis',
                               domain="[('have_reservation', '=', False), ('state', 'not in', ('cancel', 'sent', 'draft'))]",
                               readonly=True, store=True)

    num_dossier = fields.Char(related='order_id.num_dossier', readonly=True, store=True)
    date = fields.Date(related='order_id.validity_date',required=1, states={'draft': [('readonly', True)]})

    def action_validate(self):

        if self.order_id.state not in ('sale', 'done',):
            raise UserError(_('La commande n\'est pas confirmée, Veuillez la confirmer !'))
        else:
            amount_paid = self.order_id.total_paiement
            # Contrôle rajouté par Rabie Sakhri le 16/09/2021
            new_mtn_min_reserv = self.mtn_min_reserv
            for rec in self.product_ids:
                type_product = rec.name.type_id.name
                if type_product != 'Appartement' and type_product != 'Espace a aménager':
                    new_mtn_min_reserv = 100000

            if amount_paid < new_mtn_min_reserv:
                raise UserError(_(
                    'Le client a payé un montant de %s dzd qui est inférieur au seuil de validation de réservation (%s dzd)' % (
                        amount_paid, new_mtn_min_reserv)))
            else:

                self.state = 'valid'
                if self.partner_id.etat == 'Potentiel':
                    self.partner_id.etat = 'Réservataire'
                for rec in self.product_ids:
                    rec.name.client_id = self.partner_id.id
                    rec.name.etat = 'Réservé'
                    rec.name.order_id = self.order_id.id
                    rec.name.reservation_id = self.id
                    # annuler tous les autres devis
                    for devis in rec.name.line_ids:
                        if devis.order_id.name != self.order_id.name:
                            devis.order_id.action_cancel()
                            devis.order_id.motif_annulation = 'Prereservation'
                    
    def action_cancel(self, motif='Annulation', annuler_echeance=True):
        self.state = 'cancel'
        self.order_id.action_cancel()
        self.order_id.motif_annulation = motif
        # liberer les produits
        for rec in self.product_ids:
            rec.name.client_id = None
            rec.name.order_id = None
            rec.name.reservation_id = None
            rec.name.etat = 'Désistement'
        # annuler les echeances restantes
        if annuler_echeance:
            ech = self.env['crm.echeancier'].search([('order_id', '=', self.order_id.id)])
            for line in ech:
                if line.state not in 'done,open':
                    line.state = 'cancel'
                if line.state == 'open' and line.montant > 0:
                    reste_paiement = line.montant_prevu - line.montant
                    line.montant_prevu = line.montant
                    line.state = 'done'
                    self.env['crm.echeancier'].create({
                        'name': line.label + '+',
                        'order_id': ech[0].order_id.id,
                        'label': 'Annualtions et remboursements ',
                        'date_creation': date.today(),
                        'type': 'tranche',
                        'montant_prevu': reste_paiement,
                        'montant': 0.0,
                        'state': 'cancel',
                        'date_prevue': ech[0].date_prevue,
                    })
                if line.state == 'open' and line.montant <= 0:
                    line.state = 'cancel'


class CrmReservationProduct(models.Model):
    _name = 'crm.reservation.product'
    _description = 'Reservation Produit'

    project_id = fields.Many2one(related='reservation_id.project_id', string='Projet', readonly=1, store=True)
    name = fields.Many2one('product.template', string='Appartement',
                           domain="[('project_id', '=', project_id),('etat', '=', 'Libre')]")

    bloc = fields.Char(related='name.bloc', string='Bloc', readonly=1)
    type_id = fields.Many2one(related='name.type_id', string='Type du bien', readonly=1)
    format_id = fields.Many2one(related='name.format_id', string='Type', readonly=1)
    orientation = fields.Many2one(related='name.orientation', string='Orientation', readonly=1)
    etage = fields.Many2one(related='name.etage', string='Etage', readonly=1)
    superficie = fields.Float(related='name.superficie', string='Superficie', readonly=1)
    num_lot = fields.Char(related='name.num_lot', string='N° Lot', readonly=1)
    prix_m2 = fields.Float('Prix_m2', readonly=1, related='reservation_id.order_id.order_line.prix_m2', tracking=True)
    price_2 = fields.Monetary('Prix de vente', readonly=1, related='reservation_id.order_id.order_line.price_total',
                              tracking=True)
    note = fields.Char('Notes')
    reservation_id = fields.Many2one('crm.reservation', String='Reservation')
    partner_id = fields.Many2one(related='reservation_id.partner_id', string='Client', readonly=1)
    commercial_id = fields.Many2one(related='reservation_id.commercial_id', string='Commercial', readonly=1)
    charge_recouv_id = fields.Many2one(related='reservation_id.charge_recouv_id', string='Chargé de recouvrement',
                                       readonly=1)
    state = fields.Selection(related='reservation_id.state', readonly=1)
    currency_id = fields.Many2one(related='reservation_id.order_id.currency_id',
                                  depends=['reservation_id.order_id.currency_id'],
                                  store=True, string='Currency')
