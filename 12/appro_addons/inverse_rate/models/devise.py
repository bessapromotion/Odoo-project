# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Currency(models.Model):
    _inherit = "res.currency"

    rounding = fields.Float(string='Rounding Factor', digits=(16, 10), default=0.01)
    related_taux_change = fields.Float(related='rate_ids.taux_change_en_dinar')


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    taux_change_en_dinar = fields.Float(string='Taux de change actuel en dinar', digits=(12, 12), default=1.00)

    @api.onchange('taux_change_en_dinar')
    def _compute_rate(self):
        if self.taux_change_en_dinar:
            if self.currency_id.id != self.env.ref('base.DZD').id:
                self.rate = 1/self.taux_change_en_dinar
            else:
                self.rate = 1.00
                self.taux_change_en_dinar = 1.00

