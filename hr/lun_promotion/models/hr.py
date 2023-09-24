# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    @api.one
    @api.depends('promotions_ids')
    def _nbr_promotion(self):
        self.nbr_promotion = len(self.promotions_ids)

    promotions_ids = fields.One2many('hr.promotion', 'employe_id', string='Promotions')
    nbr_promotion  = fields.Integer(compute=_nbr_promotion, string='Nombre de promotions')
