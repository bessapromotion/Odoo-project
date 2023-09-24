# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'

    @api.depends('change_supercifie_ids')
    def _nbr_superficie(self):
        for rec in self:
            if self.env.user.has_group('crm_superficie.group_superficie_manager') or self.env.user.has_group('crm_superficie.group_superficie_manager'):
                rec.nbr_superficie = len(rec.change_supercifie_ids)
            else:
                rec.nbr_superficie = 0

    change_supercifie_ids = fields.One2many('crm.superficie.line', 'name', string='Changement de superficie', domain=[('action', '!=', 'noaction')])
    nbr_superficie = fields.Integer(compute=_nbr_superficie)
