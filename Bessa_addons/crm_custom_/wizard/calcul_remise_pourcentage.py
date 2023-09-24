# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date


class CaculRemisePourcentageWizard(models.TransientModel):
    _name = 'calcul.remise.pourcentage.wizard'
    _description = u'Cacule du pourcentage de la remise'
    # _order = 'hidden_number desc'

    name = fields.Many2one('sale.order.line', required=1, readonly=1,
                           default=lambda self: self.env.context['active_id'])

    prix_m2_actuel = fields.Float(related='name.prix_m2', readonly=1)
    prix_vente_actuel = fields.Float(related='name.price_unit', readonly=1)
    type = fields.Selection([('1', 'Remise sur le  Prix_m²'),
                             ('2', 'Remise sur le Prix_vente'),
                             ('3', 'Remise d\'un Montant')], string='Type de remise')
    superficie = fields.Float(related='name.superficie')
    order_id = fields.Many2one(related='name.order_id',string='Ref BC')
    currency_id = fields.Many2one(related='name.currency_id')
    project_id = fields.Many2one(related='name.project_id')
    mode_achat = fields.Selection(related='order_id.mode_achat', string='Mode Achat', readonly=1)
    nouveau_prix_m2 = fields.Float(string='Nouveau prix m²', currency_field='currency_id')
    nouveau_prix_vente = fields.Float(string='Nouveau prix de vente', currency_field='currency_id')
    amount = fields.Float(string='Montant', currency_field='currency_id')
    # residual_signed   = fields.Monetary(related='name.residual_signed', string='Reste a payer', currency_field='currency_id', readonly=True)

    discount = fields.Float('Remise (%)', currency_field='currency_id', compute='compute_discount',readonly=True)
    state = fields.Selection(
        [('draft', 'Brouillon'), ('done', 'Validée')], string='Status', default='draft', required=True, tracking=True)

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.prix_m2_actuel = self.name.prix_m2
            self.prix_vente_actuel = self.name.price_unit
            self.order_id = self.name.order_id
            self.mode_achat = self.order_id.mode_achat
            self.project_id = self.name.project_id
            self.currency_id = self.name.currency_id


    @api.depends('name', 'order_id','type','nouveau_prix_m2','nouveau_prix_vente','amount')
    def compute_discount(self):
        if self.name:
            self.discount =0
            self.onchange_name()
            if self.type == '1':
                if self.nouveau_prix_m2:
                  self.nouveau_prix_vente = self.nouveau_prix_m2 * self.superficie
            if self.type == '2':
                if self.nouveau_prix_vente:
                  self.nouveau_prix_m2 = self.nouveau_prix_vente / self.superficie
            if self.type == '3':
                if self.amount:
                  self.nouveau_prix_vente = self.prix_vente_actuel - self.amount
                  self.nouveau_prix_m2 = self.nouveau_prix_vente / self.superficie
            l =  self.prix_vente_actuel - self.nouveau_prix_vente
            self.discount = (l / self.prix_vente_actuel) * 100


    # @api.multi
    def action_appliquer(self):
        if self.discount  :
            self.name.discount = self.discount
            self.order_id.new_price_m2 = self.nouveau_prix_m2
            self.order_id.type = self.type
            self.state = 'done'
            self.order_id.discount_state = True
