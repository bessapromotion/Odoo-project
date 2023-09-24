# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Partner(models.Model):
    _name    = 'res.partner'
    _inherit = 'res.partner'

    etat  = fields.Selection([('Prospect', 'Prospect'),
                              ('Potentiel', 'Potentiel'),
                              ('Réservataire', 'Réservataire'),
                              ('Acquéreur', 'Acquéreur'),
                              ('Locataire', 'Locataire'),
                              ], string='Etat', default='Prospect', required=1)
    mode_achat = fields.Selection([('1', 'Auto'), ('2', 'Crédit'), ('3', 'Mixte'),], string='Mode Achat Probable', default='1')
    birthday   = fields.Date('Date de naissance')
    place_of_birth   = fields.Char('Lieu de naissance')
    hs_contact_id = fields.Char('HubSpot Contact ID')
    date_pi = fields.Date('Délivrée le')
    type_pi    = fields.Selection([('cin', u'Carte d\'identité nationale'),
                                   ('permis', 'Permis de conduire'),
                                   ('passport', 'Passport'),
                                   ('autre', 'Autre')], String=u'Pièce identité', default='cin', required=1)
    num_pi     = fields.Char(u'Numéro pièce d\'identité')
    code_client = fields.Integer('Code client')
    street = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one("res.country.state")
    country_id = fields.Many2one('res.country')
    mobile = fields.Char()

    @api.model
    def create(self, vals):
        if vals.get('customer') == True:
            req = "select max(code_client) as num from res_partner where customer = true"
            self._cr.execute(req)
            res = self._cr.dictfetchall()
            num = res[0].get('num')
            if not num:
                num = 1
            else:
                num += 1
            vals['code_client'] = num
            vals['ref'] = 'C' + str(num)
            if vals.get('name'):
                vals['name'] = vals['name'].upper()
        return super(Partner, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].upper()
        return super(Partner, self).write(vals)


    #Test pour l attribution de numéros aux anciens clients
    # @api.one
    # def test(self):
    #     req = "select name , code_client from res_partner where code_client = NULL ORDER BY create_date"
    #     rows=self._cr.execute(req)
    #     res = self._cr.dictfetchall()
    #     for row in res:
    #         print(row)











