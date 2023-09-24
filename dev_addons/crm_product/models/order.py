# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderSimulation(models.Model):
    _name = 'sale.order.simulation'

    name = fields.Char('Simulation')


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    @api.depends('order_line')
    def get_type_bien(self):
        for rec in self:
            rec.type_bien = ''
            if rec.order_line:
                if rec.order_line[0].product_id.type_id.name:
                    rec.type_bien = rec.order_line[0].product_id.type_id.name

    def get_invoice(self):
        for rec in self:
            rec.invoice_id = False
            invoice = self.env['account.move'].search([('invoice_origin', '=', rec.name)])
            # if invoice:
            if len(invoice) > 0:
                rec.invoice_id = invoice[0].id
            # print(invoice[0].id)
            # rec.write({'invoice_ids': [(3, invoice[0].id)]})
            # print("rec.invoice_ids")
            # print(rec.invoice_ids)

    invoice_id = fields.Many2one('account.move', compute='get_invoice', string='Facture')

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
    type_bien = fields.Char(string="Type du bien", compute='get_type_bien', store=True)
    simulation_id = fields.Many2one('sale.order.simulation', string='Etat du dossier', tracking=True)
    simulation_montant = fields.Monetary(string='Simulation')

    # @api.multi
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

        # if self.amount_total < 100.000:
        #     if not self.create_auto:
        #         print(self.name)
        #         raise UserError(_(
        #             u'Veuillez verifier le montant total de la vente'))

        return record

    @api.model
    def create(self, vals):
        print('create 1')
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
                        if (prod.client_id.etat == 'Prospect'):  # Condition rajouté par omari
                            print(prod.client_id.etat)
                            prod.client_id.etat = 'Potentiel'
                        # prod.client_id.etat = 'Potentiel'
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

    # @api.multi
    @api.onchange('partner_id')
    def change_mode_achat(self):
        self.mode_achat = self.partner_id.mode_achat

    def action_confirm(self):
        if self.num_dossier:
            rec = self.env['sale.order'].search(
                [('num_dossier', '=', self.num_dossier), ('project_id', '=', self.project_id.id),
                 ('id', '!=', self.id)])
            if rec.exists():
                raise UserError(_(
                    u'Ce numéro de dossier existe déjà dans le projet actuel, veuillez saisir un code différent'))
            else:
                return super().action_confirm()

    # @api.multi
    def action_confirm1(self):
        if self.num_dossier:
            req = "select count(num_dossier) as nbr from sale_order where num_dossier = %s and project_id=%s;"
            self._cr.execute(req, self.num_dossier, self.project_id)
            res = self._cr.dictfetchall()
            for mx in res:
                if mx.get('nbr') > 1:
                    raise UserError(_(
                        u'Ce numéro de dossier existe déjà dans le projet actuel, veuillez saisir un code différent'))

        self.action_confirm()

    # def _prepare_invoice(self):
    #     invoice_vals = super(SaleOrder, self)._prepare_invoice()
    #     if invoice_vals['journal_id'] == 3:
    #         invoice_vals['journal_id'] = 1
    #
    #     invoice_vals = {
    #         # new fields
    #         'project_id': self.project_id.id,
    #         'num_dossier': self.num_dossier,
    #         'charge_recouv_id': self.charge_recouv_id.id,
    #     }
    #     return invoice_vals

    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.move'].default_get(['journal_id'])['journal_id']
        # todo : le journal par defaut est OD (id=3) !!!! le remettre sur journal de vente (id=1) .search( journal de vente par société)
        if journal_id == 3:
            journal_id = 1

        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'ref': self.client_order_ref or '',
            'move_type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'user_id': self.user_id.id,
            'invoice_user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(
                self.partner_invoice_id.id)).id,
            'partner_bank_id': self.company_id.partner_id.bank_ids.filtered(
                lambda bank: bank.company_id.id in (self.company_id.id, False))[:1].id,
            'journal_id': journal_id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'payment_reference': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
            # new fields
            'project_id': self.project_id.id,
            'num_dossier': self.num_dossier,
            'charge_recouv_id': self.charge_recouv_id.id,
        }
        return invoice_vals


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    project_id = fields.Many2one(related='order_id.project_id', string='Projet', readonly=1, store=True)
    validity_date = fields.Date(related='order_id.validity_date', string='Date de validité', readonly=1)
    # related = 'order_id.confirmation_date',
    confirmation_date = fields.Datetime(string='Date de confirmation', readonly=1, related='order_id.date_order',
                                        store=True)
    date_order = fields.Datetime(string='Date de confirmation', readonly=1, related='order_id.date_order', store=True)
    superficie = fields.Float(related='product_id.superficie')
    num_lot = fields.Char(related='product_id.num_lot')
    type_id = fields.Many2one(related='product_id.type_id')
    format_id = fields.Many2one(related='product_id.format_id')
    orientation = fields.Many2one(related='product_id.orientation')
    prix_m2 = fields.Float('Prix m2')
    product_tmpl_id2 = fields.Many2one(related='product_id.product_tmpl_id')

    # @api.one
    def action_activate_order(self):
        self.order_id.action_draft()

    # @api.one
    def action_order_priority(self):
        self.product_id.etat = 'Pré-Réservé'
        self.product_id.client_id = self.order_partner_id.id
        self.product_id.order_id = self.order_id.id

    # @api.one
    # def action_compute_price2(self):
    #     # self.price_unit = self.product_id.price_2
    #     self.price_unit = self.superficie * self.prix_m2

    # @api.multi
    @api.onchange('name')
    def compute_price2(self):
        self.prix_m2 = self.product_id.prix_m2
        self.price_unit = self.superficie * self.prix_m2

    # @api.multi
    @api.onchange('prix_m2')
    def compute_price3(self):
        self.price_unit = self.superficie * self.prix_m2

    # @api.multi
    # @api.onchange('price_unit')
    # def price_unit_change(self):
    #     if self.product_id and self.price_unit == 0:
    #         raise UserError(
    #             _(u'Le prix du bien doit être supérier à 0.'))
