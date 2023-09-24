# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _name    = 'product.template'
    _inherit = 'product.template'

    famille_id     = fields.Many2one('product.famille', string='Famille')
    sousfamille_id = fields.Many2one('product.sousfamille', string='SousFamille')
    etat_achat     = fields.Selection([('bon', 'En cours'),
                                       ('reforme', u'A réformer'), ], default='bon', string='Etat du produit')

    @api.multi
    def action_codifier(self):
        req_1 = "select max(default_code) as mx from product_template where sousfamille_id=%s;"

        rub = (self.sousfamille_id.id,)
        self._cr.execute(req_1, rub)
        res_1 = self._cr.dictfetchall()
        if res_1[0].get('mx'):
            num = res_1[0].get('mx')
            num = "{0:0>3}".format(str(int(num[5:]) + 1))
        else:
            num = '001'

        self.default_code = self.famille_id.code + self.sousfamille_id.code + self.sousfamille_id.sequence + self.sousfamille_id.type + num
