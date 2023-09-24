# -*- coding: utf-8 -*-

from odoo import models, fields


class PartnerFormeJuridique(models.Model):
    _name = 'res.partner.forme.juridique'
    _description = 'Forme juridique'

    name = fields.Char('Forme juridique')


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    customer = fields.Boolean(string='Is a Customer', default=True,
                              help="Check this box if this contact is a customer. It can be selected in sales orders.")
    supplier = fields.Boolean(string='Est un fournisseur',
                              help="Check this box if this contact is a vendor. It can be selected in purchase orders.")

    rc  = fields.Char('RC')
    nif = fields.Char('N.I.F')
    nis = fields.Char('N.I.S')
    ai = fields.Char('AI')
    fax = fields.Char('FAX')

    type_fournisseur = fields.Selection([('Local', 'Fournisseur local'),
                                         ('Etranger', 'Fournisseur Etranger'),
                                         ('Sous-traitant', 'Sous-Traitant'),
                                         ], default='Local', string='Type fournisseur')
    forme_juridique_id = fields.Many2one('res.partner.forme.juridique', string='Forme juridique')
    supplier_user_id = fields.Many2one('res.users', string='Acheteur')