# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date


class CreerEcheancierTvaWizard(models.TransientModel):
    _name = 'creer.echeancier.tva.wizard'
    # _order = 'hidden_number desc'

    name = fields.Many2one('account.invoice', required=1, readonly=1,
                           default=lambda self: self.env.context['active_id'])
    partner_id = fields.Many2one(related='name.partner_id')
    origin = fields.Char(related='name.origin')
    order_id = fields.Many2one('sale.order', required=1)
    currency_id = fields.Many2one(related='name.currency_id')
    project_id = fields.Many2one(related='name.project_id')

    amount_total = fields.Monetary(related='name.amount_untaxed', string='Total HT', currency_field='currency_id',
                                   readonly=True)
    amount_tva = fields.Monetary(related='name.amount_tax', string='Total TVA', currency_field='currency_id',
                                 readonly=True)
    # residual_signed   = fields.Monetary(related='name.residual_signed', string='Reste a payer', currency_field='currency_id', readonly=True)

    montant_tva = fields.Float('Montant TVA', currency_field='currency_id')
    date_tva = fields.Date(u'Date premiere tva', required=1)

    montant_notaire = fields.Float('Montant a payer')
    date_notaire = fields.Date(u'Date premiere notaire', required=1)

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.montant_tva = self.name.amount_tax
            if self.name.origin:
                so = self.env['sale.order'].search([('name', '=', self.name.origin)])
                if so.exists():
                    self.order_id = so[0].id

    @api.multi
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
