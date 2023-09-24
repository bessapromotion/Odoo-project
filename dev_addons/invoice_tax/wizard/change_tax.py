# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools import conversion


class ChangeTaxWizard(models.TransientModel):
    _name = 'change.tax.wizard'

    name        = fields.Many2one('account.move', string='Facture', required=1, readonly=1, default=lambda self: self.env.context['active_id'])
    currency_id = fields.Many2one(related='name.currency_id')

    amount_total = fields.Monetary(related='name.amount_untaxed', string='Total HT', currency_field='currency_id', readonly=True)
    amount_tva   = fields.Monetary(related='name.amount_tax', string='Total TVA', currency_field='currency_id', readonly=True)

    montant_declare = fields.Monetary('Montant déclaré', currency_field='currency_id')
    tva_id = fields.Many2one('account.tax', string='Taxe')
    montant_tva = fields.Monetary('Montant TVA', currency_field='currency_id')

    @api.onchange('montant_declare', 'tva_id')
    def onchange_mtn_tva(self):
        if self.tva_id:
            self.montant_tva = self.montant_declare * self.tva_id.amount / 100
        else:
            self.montant_tva = 0.0

    # @api.multi
    def action_appliquer(self):
        decalage = self.name.amount_tax - self.montant_tva

        # changement dans la facture
        self.name.amount_declared = self.montant_declare
        self.name.amount_tax      = self.montant_tva

        self.name.amount_total                = self.montant_tva + self.amount_total
        self.name.amount_total_signed         = self.name.amount_total
        self.name.amount_total_company_signed = self.name.amount_total

        self.name.residual        = self.name.residual - decalage
        self.name.residual_signed = self.name.residual
        self.name.residual_company_signed = self.name.residual

        # table invoice taxes
        tax = self.env['account.move.tax'].search([('invoice_id', '=', self.name.id), ('tax_id', '=', self.tva_id.id)])
        if tax.exists():
            tax.amount = self.montant_tva

        # paiement echeance tva
        ech = self.env['crm.echeancier'].search([('invoice_id', '=', self.name.id), ('type', '=', 'tva')])
        if ech.exists():
            ech.montant_prevu = self.montant_tva

        # ecritures comptables

        # ech = self.env['crm.echeancier'].search([('state', '=', 'inprogress')])

        # for rec in ech:
        #     pi = 4
        #     self.env['ordre.paiement'].create({
        #         'date': rec.date_prevue,
        #         'invoice_id': rec.invoice_id.id,
        #         'echeance_id': rec.id,
        #         'commercial_id': rec.commercial_id.id,
        #         'partner_reference': '',
        #         'amount': rec.montant_prevu,
        #         'amount_lettre': conversion.conversion(rec.montant_prevu),
        #         'mode_paiement_id': pi,
        #         'objet': rec.label,
        #         # 'doc_payment_id': doc_num,
        #         'observation': rec.observation,
        #         'state': 'open',
        #     })
