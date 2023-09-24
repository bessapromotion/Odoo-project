# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class CrmPreReservation(models.Model):
    _name = 'crm.pre.reservation'
    _description = 'PreReservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name          = fields.Char('Numero', readonly=1)
    project_id    = fields.Many2one('project.project', string='Projet')
    product_id    = fields.Many2one('product.template', string='Bien affecté', required=1)
    bloc          = fields.Char(related='product_id.bloc', string='Bloc', readonly=1)
    type_id       = fields.Many2one(related='product_id.type_id', string='Type du bien', readonly=1)
    format_id     = fields.Many2one(related='product_id.format_id', string='Type', readonly=1)
    orientation   = fields.Many2one(related='product_id.orientation', string='Orientation', readonly=1)
    etage         = fields.Many2one(related='product_id.etage', string='Etage', readonly=1)
    superficie    = fields.Float(related='product_id.superficie', string='Superficie', readonly=1)
    prix_m2       = fields.Float(related='product_id.prix_m2', string='Prix m2', readonly=1)
    price_2       = fields.Float(related='product_id.price_2', string='Prix vente', readonly=1)
    client_id     = fields.Many2one(related='product_id.client_id', string='Client', readonly=1)
    order_id      = fields.Many2one(related='product_id.order_id', string='Préservation', readonly=1)

    new_order_id  = fields.Many2one('sale.order', string='Nouvelle PréRéservation', required=1, readonly=1, states={'draft': [('readonly', False)]})
    new_partner_id= fields.Many2one(related='new_order_id.partner_id', string='Nouveau Client préaffecté', required=1, readonly=1)

    date          = fields.Date('Date', readonly=1, required=1, states={'draft': [('readonly', False)]}, default=date.today())
    commercial_id = fields.Many2one('res.users', required=1, string='Commercial', readonly=1, states={'draft': [('readonly', False)]})
    observation   = fields.Text('Observation')
    motif         = fields.Text('Motif')
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', 'Validée'),
                              ('cancel', 'Annulée'), ], string='Etat', default='draft', tracking=True)
    company_id = fields.Many2one('res.company', u'Société', related='project_id.company_id', store=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('crm.pre.reservation') or '/'

        return super(CrmPreReservation, self).create(vals)

    # @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Suppression non autorisée ! \n\n  Le document est déjà validée !'))
        else:

            rec = super(CrmPreReservation, self).unlink()
            return rec

    # @api.one
    def action_cancel(self):
        self.state = 'cancel'

    # @api.one
    def action_validate(self):
        self.state = 'valid'
        self.new_partner_id.etat = 'Réservataire'

        self.product_id.client_id = self.new_partner_id.id
        self.product_id.etat = 'Pré-Réservé'
        self.product_id.order_id = self.new_order_id.id
        # rec.name.reservation_id = self.id
        # annuler tous les autres devis
        # for devis in self.product_id.line_ids:
        #     if devis.order_id.name != self.new_order_id.name:
        #         devis.order_id.state = 'cancel'
