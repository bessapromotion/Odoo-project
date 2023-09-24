# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import date
from lxml import etree


class Depense(models.Model):
    _name = 'crm.depense'
    _inherit = 'crm.depense'

    caisse_id = fields.Many2one('crm.caisse', string='Caisse', store=True)

    # @api.one
    # def action_validate(self):
    #    if self.date:
    #       rec = self.env['crm.caisse'].search(
    #           [('date_today', '=', self.date), ('company_id', '=', self.company_id.id)])
    #      print(rec.id)
    #        if rec.exists():
    #            self.state = 'valid'
    #            self.set_tags()
    #            for tag in self.tags_ids:
    #                print(tag.name)
    #            if not self.benificiaire and self.employee_id:
    #                self.benificiaire = self.employee_id.name
    #        else:
    #            raise UserError(_(
    #                u'La caisse de cette journée n\'existe pas, Veuillez la creer Puis valider cette dépense '))
