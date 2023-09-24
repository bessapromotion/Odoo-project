# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmReservation(models.Model):
    _inherit = 'crm.reservation'

    superficie_id = fields.Many2one('crm.superficie', string='Changement superficie', readonly=1)
