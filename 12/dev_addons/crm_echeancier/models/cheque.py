# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PaymentDoc(models.Model):
    _name = 'payment.doc'
    _description = 'Documents de paiement'

    name             = fields.Char(u'Numéro', required=True)
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement', required=True)
    domiciliation    = fields.Char('Domiciliation')
    ordonateur       = fields.Char('Ordonateur')
    date             = fields.Date(u'Date')
    objet            = fields.Selection([('normalise','NORMALISE'),('avance', 'AVANCE')] , string='Objet de Chèque')
    type             = fields.Selection([('no_certifie', 'NON CERTIFIE'), ('certifie', 'CERTIFIE'), ('credit', 'CHEQUE CREDIT')] ,string ='Type de Chèque')

    @api.multi
    def name_get(self):
        return [(i.id, i.mode_paiement_id.name + ' # ' + i.name) for i in self]
