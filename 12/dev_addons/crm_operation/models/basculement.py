# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class CrmBasculement(models.Model):
    _name = 'crm.basculement'
    _description = 'Basculement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    @api.depends('a_price_2', 'total_paiement')
    def _reste_paiement(self):
        for rec in self:
            rec.reste_paiement = rec.a_price_2 - rec.total_paiement

    name           = fields.Char('Numero', readonly=1)
    commercial_id = fields.Many2one('res.users', required=1, string='Commercial', readonly=1,
                                    states={'draft': [('readonly', False)]})
    charge_recouv_id = fields.Many2one('res.users', required=1, string='Chargé de Recouvrement', readonly=1,
                                       states={'draft': [('readonly', False)]})
    date   = fields.Date('Date', required=1, default=date.today())
    motif = fields.Text('Motif')
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', 'Validée'),
                              ('cancel', 'Annulée'), ], string='Etat', default='draft', track_visibility='onchange')

    reservation_id = fields.Many2one('crm.reservation', string='Réservation', required=True)
    product_ids    = fields.Many2one('crm.reservation.product', string='Bien(s)')
    partner_id     = fields.Many2one(related='reservation_id.partner_id', string='Client', readonly=1, store=True)
    phone          = fields.Char(related='partner_id.phone', string='Téléphone', readonly=1)
    mobile         = fields.Char(related='partner_id.mobile', string='Mobile', readonly=1)
    photo          = fields.Binary(related='partner_id.image', string='Photo')
    date_reservation = fields.Date(related='reservation_id.date', string=u'Date réservation', readonly=1, store=True)
# A
    a_project_id   = fields.Many2one(related='reservation_id.project_id', string='Projet', readonly=1, store=True)
    a_product_id   = fields.Many2one('product.template', string='Bien affecté', required=1)
    a_bloc         = fields.Char(related='a_product_id.bloc', string='Bloc', readonly=1)
    a_type_id      = fields.Many2one(related='a_product_id.type_id', string='Type du bien', readonly=1)
    a_format_id    = fields.Many2one(related='a_product_id.format_id', string='Type', readonly=1)
    a_orientation  = fields.Many2one(related='a_product_id.orientation', string='Orientation', readonly=1)
    a_etage        = fields.Many2one(related='a_product_id.etage', string='Etage', readonly=1)
    a_superficie   = fields.Float(related='a_product_id.superficie', string='Superficie', readonly=1)
    a_prix_m2      = fields.Float(related='a_product_id.prix_m2', string='Prix m2', readonly=1)
    a_price_2      = fields.Float(related='a_product_id.price_2', string='Prix vente', readonly=1)
# B
    b_project_id   = fields.Many2one('project.project', string='nouveau Projet', required=1, store=True)
    b_product_id   = fields.Many2one('product.template', string='Nouvelle affectation', required=1, store=True)
    b_bloc         = fields.Char(related='b_product_id.bloc', string='Bloc', readonly=1)
    b_type_id      = fields.Many2one(related='b_product_id.type_id', string='Nouveau type du bien', readonly=1)
    b_format_id    = fields.Many2one(related='b_product_id.format_id', string='Type', readonly=1)
    b_orientation  = fields.Many2one(related='b_product_id.orientation', string='Orientation', readonly=1)
    b_etage        = fields.Many2one(related='b_product_id.etage', string='Etage', readonly=1)
    b_superficie   = fields.Float(related='b_product_id.superficie', string='Superficie', readonly=1)
    b_prix_m2      = fields.Float(related='b_product_id.prix_m2', string='Prix m2', readonly=1)
    b_price_2      = fields.Float(related='b_product_id.price_2', string='Prix vente', readonly=1)

# info
    order_id       = fields.Many2one(related='reservation_id.order_id', string='Commande')
    prix_vente     = fields.Monetary(related='order_id.amount_untaxed')
    total_paiement = fields.Monetary(related='order_id.total_paiement', string='Montant versé')
    currency_id    = fields.Many2one(related='reservation_id.order_id.currency_id', string='Devise')
    reste_paiement = fields.Monetary(compute=_reste_paiement, string='Reste a payer')

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

    @api.one
    def action_validate(self):
        self.state = 'valid'

        self.b_product_id.client_id = self.partner_id.id
        self.b_product_id.etat = self.a_product_id.etat
        self.a_product_id.client_id = None
        self.a_product_id.etat = 'Libre'

    @api.onchange('reservation_id')
    def onchange_reservation(self):
        if self.reservation_id:
            self.commercial_id = self.reservation_id.commercial_id.id
            self.charge_recouv_id = self.reservation_id.charge_recouv_id.id
            self.total_paiement = self.reservation_id.total_paiement
            if len(self.reservation_id.product_ids) == 1:
                self.product_ids = self.reservation_id.product_ids[0]
        else:
            self.commercial_id = None
            self.charge_recouv_id = None
            self.product_ids = None

    @api.onchange('product_ids')
    def onchange_product_ids(self):
        if self.product_ids:
            self.a_product_id = self.product_ids.name
        else:
            self.a_project_id = None
            self.a_bloc = None
            self.a_etage = None
            self.a_format_id = None
            self.a_orientation = None
            self.a_superficie = None
            self.a_prix_m2 = None
            self.a_price_2 = None
