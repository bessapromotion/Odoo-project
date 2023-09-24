# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date


class CreerEcheancierTvaWizard(models.TransientModel):
    _inherit = 'creer.echeancier.tva.wizard'
 

    name = fields.Many2one('account.move', required=1, readonly=1,
                           default=lambda self: self.env.context['active_id'])
    partner_id = fields.Many2one(related='name.partner_id')
    origin = fields.Char(related='name.invoice_origin')
    order_id = fields.Many2one('sale.order', required=1)
    currency_id = fields.Many2one(related='name.currency_id')
    project_id = fields.Many2one(related='name.project_id')
    mode_achat = fields.Selection(related='order_id.mode_achat', string='Mode Achat', readonly=1)
    amount_total = fields.Monetary(related='name.amount_untaxed', string='Total HT', currency_field='currency_id',
                                   readonly=True)
    amount_tva = fields.Monetary(related='name.amount_tax', string='Total TVA', currency_field='currency_id',
                                 readonly=True)
    amount_ttc = fields.Monetary(related='name.amount_total', string='Total TTC', currency_field='currency_id',
                                 readonly=True)
    # residual_signed   = fields.Monetary(related='name.residual_signed', string='Reste a payer', currency_field='currency_id', readonly=True)

    montant_tva = fields.Monetary('Montant TVA', currency_field='currency_id', compute='compute_tva_notaire', readonly=True)
    date_tva = fields.Date(u'Date premiere tva', required=1)

    montant_notaire = fields.Monetary('Montant a payer', currency_field='currency_id', compute='compute_tva_notaire')
    date_notaire = fields.Date(u'Date premiere notaire', required=1)
    

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.montant_tva = self.name.amount_tax

            if self.name.invoice_origin:
                so = self.env['sale.order'].search([('name', '=', self.name.invoice_origin)])
                if so.exists():
                    self.order_id = so[0].id
                    self.mode_achat = self.order_id.mode_achat

    @api.depends('name', 'order_id')
    def compute_tva_notaire(self):
        if self.name:
            self.onchange_name()
            print("compute_tva_notair",self.mode_achat)
            self.montant_tva = self.name.amount_tax
            if self.amount_ttc:
                mode_achat = self.mode_achat
                print(mode_achat,type(mode_achat))
                condition = ( self.mode_achat == '1')
                print("condition", condition)
                if self.mode_achat == '1':
                    print(self.montant_notaire)
                    self.montant_notaire = 0.0219 * self.name.amount_total + 15000
                    print(self.montant_notaire)
                if self.mode_achat == '2' or self.mode_achat == '3':
                    print("2")
                    self.montant_notaire = 0.0219 * self.name.amount_total + 27000

    # @api.multi
    def action_appliquer(self):
        if self.montant_tva > 0.0:
            self.env['crm.echeancier'].create({
                'name': '#TVA',
                'order_id': self.order_id.id,
                'label': 'Paiement de la TVA',
                'date_creation': date.today(),
                'date_prevue': self.date_tva,
                'montant_prevu': self.montant_tva,
                'type': 'tva',
                'montant': 0.0,
            })

        if self.montant_notaire > 0.0:
            self.env['crm.echeancier'].create({
                'name': '#Notaire',
                'order_id': self.order_id.id,
                'label': 'Paiement du notaire',
                'date_creation': date.today(),
                'date_prevue': self.date_notaire,
                'montant_prevu': self.montant_notaire,
                'type': 'notaire',
                'montant': 0.0,
            })
        self.name.echeance_ok = True
        return True
