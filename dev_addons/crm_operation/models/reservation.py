# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class CrmReservation(models.Model):
    _name = 'crm.reservation'
    _description = 'Reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char('Numero', readonly=1)
    partner_id = fields.Many2one('res.partner', string='Client', required=1, readonly=1,
                                 states={'draft': [('readonly', False)]})
    mode_achat = fields.Selection(related='partner_id.mode_achat', string='Mode Achat', readonly=True, store=True)
    phone = fields.Char(related='partner_id.phone', string='Téléphone', readonly=1)
    mobile = fields.Char(related='partner_id.mobile', string='Mobile', readonly=1)
    photo = fields.Binary(related='partner_id.image_1920', string='Photo')
    product_ids = fields.One2many('crm.reservation.product', 'reservation_id', string='Appartement', readonly=1,
                                  states={'draft': [('readonly', False)]})
    project_id = fields.Many2one('project.project', string='Projet', readonly=1,
                                 states={'draft': [('readonly', False)]})
    date = fields.Date('Date', readonly=1, required=1, states={'draft': [('readonly', False)]}, default=date.today())
    date_limite = fields.Date('Date limite', required=1)
    commercial_id = fields.Many2one('res.users', required=0, string='Commercial', readonly=1,
                                    states={'draft': [('readonly', False)]})
    charge_recouv_id = fields.Many2one('res.users', required=1, string='Chargé de Recouvrement', readonly=1,
                                       states={'draft': [('readonly', False)]})
    observation = fields.Text('Observation')
    opportunity_id = fields.Many2one('crm.lead', string='Opportunité')
    order_id = fields.Many2one('sale.order', string='Associer un devis',
                               domain="[('have_reservation', '=', False), ('state', 'not in', ('cancel', 'sent', 'draft'))]")
    invoice_id = fields.Many2one('account.move', string='Facture')
    # echeancier_ids  = fields.One2many(related='invoice_id.echeancier_ids', string='Echeances')
    mtn_min_reserv = fields.Float('Montant min')
    mtn_min_print = fields.Float('Pourcentage min')
    state = fields.Selection([('draft', 'Nouvelle'),
                              ('valid', 'Validée'),
                              ('bascul', 'Basculée'),
                              ('cancel', 'Annulée'), ], string='Etat', default='draft', tracking=True)
    num_dossier = fields.Char('N° Dossier')
    basculement_dst_id = fields.Many2one('crm.reservation', string='Basculée vers', readonly=1)
    basculement_src_id = fields.Many2one('crm.reservation', string='Basculée depuis', readonly=1)

    street = fields.Char(related='partner_id.street', string='Adresse')
    company_id = fields.Many2one('res.company', u'Société', related='project_id.company_id', store=True)
    type_bien = fields.Char(string="Type du bien", related='order_id.type_bien', store=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('crm.reservation') or '/'
        return super(CrmReservation, self).create(vals)

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Suppression non autorisée ! \n\n  La réservation est déjà validée !'))
        else:
            self.product_ids.unlink()

            rec = super(CrmReservation, self).unlink()
            return rec

    def action_cancel(self, motif='Annulation', annuler_echeance=True):
        self.state = 'cancel'
        self.order_id.action_cancel()
        self.order_id.motif_annulation = motif
        # liberer les produits
        for rec in self.product_ids:
            rec.name.client_id = None
            rec.name.order_id = None
            rec.name.reservation_id = None
            rec.name.etat = 'Libre'
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

    @api.onchange('order_id')
    def onchange_devis(self):
        if self.order_id:
            self.partner_id = self.order_id.partner_id.id
            self.commercial_id = self.order_id.user_id.id
            self.opportunity_id = self.order_id.opportunity_id.id
            self.project_id = self.order_id.project_id.id
            self.num_dossier = self.order_id.num_dossier
            lines = []
            for rec in self.order_id.order_line:
                self.env['crm.reservation.product'].create({
                    'name': rec.product_id.product_tmpl_id.id,
                    'reservation_id': self.id,
                    'prix_m2': rec.prix_m2,
                    'price_2': rec.price_unit,
                })

    def print_reservation(self):

        amount_paid = self.order_id.total_paiement
        seuil = self.order_id.amount_untaxed * self.mtn_min_print / 100
        if amount_paid < seuil:
            raise UserError(_(
                'le client a payé un montant de %s qui est inférieur à %s  pourcent du prix de vente [%s dzd]' % (
                    amount_paid, self.mtn_min_print * 100, seuil)))
        else:
            return self.env.ref('crm_operation.act_report_reservation').with_context(
                {'discard_logo_check': True}).report_action(self)


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
    prix_m2 = fields.Float('Prix_m2', readonly=1, related='name.prix_m2')
    price_2 = fields.Float('Prix de vente', readonly=1, related='name.price_2')
    note = fields.Char('Notes')
    reservation_id = fields.Many2one('crm.reservation', String='Reservation')
    partner_id = fields.Many2one(related='reservation_id.partner_id', string='Client', readonly=1)
    commercial_id = fields.Many2one(related='reservation_id.commercial_id', string='Commercial', readonly=1)
    charge_recouv_id = fields.Many2one(related='reservation_id.charge_recouv_id', string='Chargé de recouvrement',
                                       readonly=1)
    state = fields.Selection(related='reservation_id.state', readonly=1)
