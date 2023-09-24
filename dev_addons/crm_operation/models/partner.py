# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    # @api.one
    @api.depends('reservation_ids')
    def _nbr_reservation(self):
        for rec in self:
            nbr = 0
            for line in rec.reservation_ids:
                if line.state in ('draft', 'valid',):
                    nbr += 1
            rec.nbr_reservation = nbr

    reservation_ids = fields.One2many('crm.reservation', 'partner_id', string='Reservation')
    nbr_reservation = fields.Integer(compute=_nbr_reservation, string='Reservations')
