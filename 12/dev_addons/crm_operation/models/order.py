# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

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

    @api.one
    @api.depends('reservation_ids')
    def _nbr_reservation(self):
        for rec in self:
            rec.nbr_reservation = len(rec.reservation_ids)

    reservation_ids  = fields.One2many('crm.reservation', 'order_id', string='Réservation')
    have_reservation = fields.Boolean(compute=_have_reservation, string='A une réservation')
    nbr_reservation  = fields.Integer(compute=_nbr_reservation, string='Réservations')
    motif_annulation = fields.Selection([('Basculement', 'Basculement'),
                                         ('Annulation', 'Annulation'),
                                         ('Prereservation', 'Annulation préréservation')], string='Motif annulation')

    num_pi     = fields.Char(related='partner_id.num_pi', string='Num pièce', help='Numéro de la pièce')
    date_pi    = fields.Date(related='partner_id.date_pi', string='Date Délivrance')
    street     = fields.Char(related='partner_id.street', string='Adresse', help='Adresse')
    ref        = fields.Char(related='partner_id.ref', string='Ref Client', help='Réference client : \n C : Client ordinaire \n P : Client privilégié \n B : Client BPI \n')
