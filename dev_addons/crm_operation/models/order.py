# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'


    #
    invoice_ids = fields.Many2many("account.move", string='Invoices', copy=False, readonly=False, )

    # invoice_count = fields.Integer(string='Invoice Count', compute='recuper_invoice', store=True)
    #
    # def recuper_invoice(self):
    #     # sales = self.env['sale.order'].search([])
    #     # if sales:
    #     for rec in self:
    #         invoice = self.env['account.move'].search([('invoice_origin', '=', rec.name)])
    #         if invoice:
    #             rec.invoice_ids = invoice
    #             rec.invoice_count = len(invoice)
    #             for inv in rec.invoice_ids:
    #                 print('inv.name', inv.name)

    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)

        self.with_context(context)._action_confirm()
        # if self.env.user.has_group('sale.group_auto_done_setting'):
        #     self.action_done()
        return True

    @api.depends('reservation_ids')
    def _have_reservation(self):
        for rec in self:
            nbr = 0
            for line in rec.reservation_ids:
                if line.state != 'cancel':
                    nbr += 1
            if nbr > 0:
                rec.have_reservation = True
            else:
                rec.have_reservation = False

    # @api.one
    @api.depends('reservation_ids')
    def _nbr_reservation(self):
        for rec in self:
            rec.nbr_reservation = len(rec.reservation_ids)

    reservation_ids = fields.One2many('crm.reservation', 'order_id', string='Réservation')
    have_reservation = fields.Boolean(compute=_have_reservation, string='A une réservation', store=True)
    nbr_reservation = fields.Integer(compute=_nbr_reservation, string='Réservations')
    motif_annulation = fields.Selection([('Basculement', 'Basculement'),
                                         ('Annulation', 'Annulation'),
                                         ('Prereservation', 'Annulation préréservation')], string='Motif annulation')

    num_pi = fields.Char(related='partner_id.num_pi', string='Num pièce', help='Numéro de la pièce')
    date_pi = fields.Date(related='partner_id.date_pi', string='Date Délivrance')
    street = fields.Char(related='partner_id.street', string='Adresse', help='Adresse')
    ref = fields.Char(related='partner_id.ref', string='Ref Client',
                      help='Réference client : \n C : Client ordinaire \n P : Client privilégié \n B : Client BPI \n')
