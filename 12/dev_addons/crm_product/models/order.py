# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    project_id = fields.Many2one('project.project', string='Projet', readonly=1,
                                 states={'draft': [('readonly', False)]}, required=1)
    mode_achat = fields.Selection([('1', 'Auto'), ('2', 'Crédit'), ('3', 'Mixte'), ], string='Mode Achat', default='1')
    validity_date = fields.Date(required=1)
    num_dossier = fields.Char(u'N° Dossier', required=1)
    auxiliaire_cpt = fields.Char(u'Auxiliaire compta')
    create_auto = fields.Boolean('devis créé automatiquement', default=False)

    payment_term_id = fields.Many2one('account.payment.term', required=1)
    charge_recouv_id = fields.Many2one('res.users', string=u'Recouvrement', required=1,
                                       default=lambda self: self.env.user)

    @api.multi
    def write(self, vals):
        record = super(SaleOrder, self).write(vals)
        if vals.get('num_dossier'):
            req = "select count(num_dossier) as nbr from sale_order where num_dossier = %s and project_id=%s;"
            pr = self.project_id.id
            self._cr.execute(req, (vals.get('num_dossier'), pr))
            res = self._cr.dictfetchall()
            for mx in res:
                if mx.get('nbr') > 1:
                    raise UserError(_(
                        u'Ce numéro de dossier existe déjà dans le projet actuel, veuillez saisir un code différent'))

        if self.order_line:
            print('ok')
        else:
            if not self.create_auto:
                raise UserError(_(
                    u'Préréservation vide, veuillez sélectionner les biens à proposer au client'))

        if self.amount_total < 100.000:
            if not self.create_auto:
                raise UserError(_(
                    u'Veuillez verifier le montant total de la vente'))

        return record

    @api.model
    def create(self, vals):
        # Override the original create function for the res.partner model
        record = super(SaleOrder, self).create(vals)

        if vals.get('num_dossier'):
            req = "select count(num_dossier) as nbr from sale_order where num_dossier = %s and project_id=%s;"
            self._cr.execute(req, (vals.get('num_dossier'), vals.get('project_id')))
            res = self._cr.dictfetchall()
            for mx in res:
                if mx.get('nbr') > 1:
                    raise UserError(_(
                        u'Ce numéro de dossier existe déjà dans le projet actuel, veuillez saisir un code différent'))
        total = 0.0
        if vals.get('order_line'):

            for rec in vals['order_line']:
                total += rec[2].get('price_unit')
                prod = self.env['product.product'].browse(rec[2].get('product_id'))
                if prod.exists():
                    if len(prod.line_ids) == 1:
                        prod.etat = 'Pré-Réservé'
                        prod.client_id = vals['partner_id']
                        prod.client_id.etat = 'Potentiel'
                        prod.order_id = record.id
        else:
            if not vals.get('create_auto'):
                raise UserError(_(
                    u'Préréservation vide, veuillez sélectionner les biens à proposer au client'))

        if total < 100:
            if not vals.get('create_auto'):
                raise UserError(_(
                    u'Veuillez verifier le montant total de la vente'))

        return record

    @api.multi
    @api.onchange('partner_id')
    def change_mode_achat(self):
        self.mode_achat = self.partner_id.mode_achat

    @api.multi
    def action_confirm1(self):
        self.action_confirm()

    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'project_id': self.project_id.id,
            'num_dossier': self.num_dossier,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'charge_recouv_id': self.charge_recouv_id.id,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
        }
        return invoice_vals


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    project_id = fields.Many2one(related='order_id.project_id', string='Projet', readonly=1)
    validity_date = fields.Date(related='order_id.validity_date', string='Date de validité', readonly=1)
    confirmation_date = fields.Datetime(related='order_id.confirmation_date', string='Date de confirmation', readonly=1)
    superficie = fields.Float(related='product_id.superficie')
    num_lot = fields.Char(related='product_id.num_lot')
    type_id = fields.Many2one(related='product_id.type_id')
    format_id = fields.Many2one(related='product_id.format_id')
    orientation = fields.Many2one(related='product_id.orientation')
    prix_m2 = fields.Float('Prix m2')
    product_tmpl_id2 = fields.Many2one(related='product_id.product_tmpl_id')

    @api.one
    def action_activate_order(self):
        self.order_id.action_draft()

    @api.one
    def action_order_priority(self):
        self.product_id.etat = 'Pré-Réservé'
        self.product_id.client_id = self.order_partner_id.id
        self.product_id.order_id = self.order_id.id

    # @api.one
    # def action_compute_price2(self):
    #     # self.price_unit = self.product_id.price_2
    #     self.price_unit = self.superficie * self.prix_m2

    @api.multi
    @api.onchange('name')
    def compute_price2(self):
        self.prix_m2 = self.product_id.prix_m2
        self.price_unit = self.superficie * self.prix_m2

    @api.multi
    @api.onchange('prix_m2')
    def compute_price3(self):
        self.price_unit = self.superficie * self.prix_m2

