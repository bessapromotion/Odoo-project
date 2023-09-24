# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
#
# Copyright (c) 2016  - Osis - www.osis-dz.net

from odoo import fields, models, api
from odoo.osv import expression


class ResCommune(models.Model):
    _name = 'res.commune'
    _descritpion = 'Commune'
    _order = 'name,id'

    code = fields.Char(string='Code Commune', size=2, help='Le code de la commune sur deux positions', required=True)
    state_id = fields.Many2one('res.country.state', string='Wilaya', required=True)
    wcode = fields.Char(related='state_id.code', readonly=1)
    name = fields.Char(string='Commune', size=64, required=True)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if self.env.context.get('state_id'):
            args = expression.AND([args, [('state_id', '=', self.env.context.get('state_id'))]])

        if operator == 'ilike' and not (name or '').strip():
            first_domain = []
            domain = []
        else:
            first_domain = [('wcode', '=ilike', name)]
            domain = [('name', operator, name)]

        first_com_ids = self._search(expression.AND([first_domain, args]), limit=limit, access_rights_uid=name_get_uid) if first_domain else []
        # com_ids = first_com_ids + [commune_id for commune_id in self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid) if not commune_id in first_com_ids]

        return list(first_com_ids) + [
            commune_id
            for commune_id in self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid) if commune_id not in first_com_ids
        ]
        # return models.lazy_name_get(self.browse(com_ids).with_user(name_get_uid))

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} ({})".format(record.name, record.state_id.code)))
        return result


class ResPartner(models.Model):
    _inherit = 'res.partner'

    commune_id = fields.Many2one('res.commune', string='Commune')

    @api.onchange('commune_id')
    def commune_id_change(self):
        if not self.state_id:
            self.state_id = self.commune_id.state_id.id
            # partner.city = partner.commune_id.name
            self.country_id = self.commune_id.state_id.country_id.id

    @api.onchange('state_id')
    def state_id_change(self):
        res = {'domain': {'commune_id': []}}
        if self.state_id:
            self.commune_id = False
            res['domain']['commune_id'] = [('state_id', '=', self.state_id.id)]
        return res


