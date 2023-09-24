# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.tools import conversion
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _name    = 'purchase.order'
    _inherit = 'purchase.order'

    @api.one
    @api.depends('payment_term_id','amount_total')
    def _amount_timbre(self):
        for order in self:
            amount_timbre = order.amount_total
            if order.payment_term_id and order.payment_term_id.payment_type == 'cash':
                timbre = self.env['config.timbre']._timbre(order.amount_total)
                self.timbre = timbre['timbre']
                amount_timbre = timbre['amount_timbre']
            self.amount_timbre = amount_timbre

    @api.onchange('payment_term_id')
    def onchange_payment_term(self):
        if not self.payment_term_id:
            self.update({
                'payment_type': False,
            })
            return
        values = {
            'payment_type': self.payment_term_id and self.payment_term_id.payment_type or False,
        }
        self.update(values)

    @api.one
    @api.depends('order_line','payment_term_id')
    def _display_Number_To_Word_timbre(self):
        # raise UserError(_('Erreur!'))
        if self.payment_term_id and self.payment_term_id.payment_type == 'cash':
            self.montant_lettre = conversion.conversion(self.amount_timbre)
        else:
            self.montant_lettre = conversion.conversion(self.amount_total)
        # return super(PurchaseOrder, self)._display_Number_To_Word()

    payment_type   = fields.Char('Type de paiement')
    timbre         = fields.Monetary(string='Timbre', store=True, readonly=True,
                             compute='_amount_timbre', track_visibility='always')
    amount_timbre  = fields.Monetary(string='Total avec Timbre', store=True,
                                    readonly=True, compute='_amount_timbre', track_visibility='always')
    montant_lettre = fields.Text(compute=_display_Number_To_Word_timbre, string='Montant lettre')


class AccountInnvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('payment_term_id','amount_total')
    def _amount_timbre(self):
        for order in self:
            amount_timbre = order.amount_total
            if order.payment_term_id and order.payment_term_id.payment_type == 'cash':
               timbre = self.env['config.timbre']._timbre(order.amount_total)
               self.timbre = timbre['timbre']
               amount_timbre = timbre['amount_timbre']
            self.amount_timbre = amount_timbre

    @api.onchange('payment_term_id')
    def onchange_payment_term(self):
        if not self.payment_term_id:
            self.update({
                'payment_type': False,
            })
            return
        values = {
            'payment_type': self.payment_term_id and self.payment_term_id.payment_type or False,
        }
        self.update(values)

    payment_type = fields.Char('Type de paiement')
    timbre = fields.Monetary(string='Timbre', store=True, readonly=True,
                             compute='_amount_timbre', track_visibility='always')
    amount_timbre = fields.Monetary(string='Total avec Timbre', store=True,
                                    readonly=True, compute='_amount_timbre', track_visibility='always')

