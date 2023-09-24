# -*- coding: utf-8 -*-


from odoo import fields, models, api
import calendar
from datetime import datetime as dt


class ProductCodificationCorrection(models.Model):
    _name = 'product.codification.correction'
    _description = 'Correction codification produit'
    _order = 'name desc'

    name = fields.Char('Description')
    date = fields.Date('Date')
    # famille_id = fields.Many2one('product.famille', string='Famille', required=True)
    # sousfamille_id = fields.Many2one('product.sousfamille', string='SousFamille', required=True)
    state = fields.Selection([('famille', u'1- Code erroné'), ('double', '2- Double'), ('vide', '3- Code vide'), ('done', u'Terminé') ], string='Action', default='famille')
    note = fields.Text('Note')
    line_ids = fields.One2many('product.codification.correction.line', 'correction_id')

    def search_code_famille(self):
        self.line_ids.unlink()
        lst = self.env['product.product'].search([('purchase_ok', '=', True), ('default_code', '!=', False)])
        for rec in lst:
            if rec.default_code[0:1] != rec.product_tmpl_id.famille_id.code:
                self.env['product.codification.correction.line'].create({
                    'name': rec.id,
                    'correction_id': self.id,
                    'old_code': rec.default_code,
                    'note': 'Code famille erroné [' + rec.default_code[0:1] + '] au lieu de [' + rec.product_tmpl_id.famille_id.code + ']'
                })

            if rec.default_code[1:3] != rec.product_tmpl_id.sousfamille_id.code:
                self.env['product.codification.correction.line'].create({
                    'name': rec.id,
                    'correction_id': self.id,
                    'old_code': rec.default_code,
                    'note': 'Code sous famille erroné [' + rec.default_code[1:3] + '] au lieu de [' + rec.product_tmpl_id.sousfamille_id.code + ']'
                })

        if len(self.line_ids) == 0:
            self.state = 'double'

    def passer_1(self):
        self.state = 'double'

    def search_double(self):
        self.line_ids.unlink()
        req = "select count(product_product.default_code) as nb,product_product.default_code from product_product, product_template " \
            "where product_product.default_code is not null " \
            "and product_template.purchase_ok = %s " \
            "and product_template.id = product_tmpl_id and product_product.active = true " \
            "group by product_product.default_code order by nb desc"

        self._cr.execute(req, (True, ))
        res = self._cr.dictfetchall()
        for rec in res:
            i = rec.get('nb')
            if rec.get('nb') > 1:
                lst = self.env['product.product'].search([('default_code', '=', rec.get('default_code')), ('purchase_ok', '=', True)])
                for line in lst:
                    self.env['product.codification.correction.line'].create({
                        'name': line.id,
                        'correction_id': self.id,
                        'old_code': line.default_code,
                        'note': 'Code en double (' + str(rec.get('nb')) + ')'
                    })

        if len(self.line_ids) == 0:
            self.state = 'vide'

    def search_code_vide(self):
        self.line_ids.unlink()
        lst = self.env['product.product'].search([('purchase_ok', '=', True), ('default_code', '=', False)])
        for rec in lst:
            note = ''
            if not rec.product_tmpl_id.famille_id:
                note = ' / sans famille'
            if not rec.product_tmpl_id.sousfamille_id:
                note += ' / sans sous famille'
            self.env['product.codification.correction.line'].create({
                'name': rec.id,
                'correction_id': self.id,
                # 'old_code': rec.default_code,
                'note': 'Code vide' + note
            })

        if len(self.line_ids) == 0:
            self.state = 'done'

    def get_code(self, product):
        req_1 = "select max(default_code) as mx from product_template where sousfamille_id=%s and active=true and LEFT(default_code, 5) = %s;"
        rub = (product.sousfamille_id.id, product.famille_id.code + product.sousfamille_id.code + product.sousfamille_id.sequence + product.sousfamille_id.type)
        self._cr.execute(req_1, rub)
        res_1 = self._cr.dictfetchall()
        if res_1[0].get('mx'):
            num = int(res_1[0].get('mx')[5:]) + 1
        else:
            num = 1

        return num

    def correction_code(self):

        for rec in self.line_ids:
            if rec.famille_id and rec.sousfamille_id:
                # num = self.get_code(rec.name.product_tmpl_id) + len(self.line_ids.filtred(lambda mo: mo.sousfamille_id == rec.sousfamille_id and mo.default_code != False))
                num = self.get_code(rec.name.product_tmpl_id) + len(self.env['product.codification.correction.line'].search([('correction_id', '=', self.id), ('sousfamille_id', '=', rec.sousfamille_id.id), ('default_code', '!=', False)]))
                rec.name.default_code = rec.famille_id.code + rec.sousfamille_id.code + rec.sousfamille_id.sequence + rec.sousfamille_id.type + "{0:0>3}".format(str(num))
            # rec.name.default_code = rec.name.famille_id.code + rec.name.sousfamille_id.code + rec.name.sousfamille_id.sequence + rec.name.sousfamille_id.type + "{0:0>3}".format(i)
            # i += 1


class ProductionCodificationCorrectionLine(models.Model):
    _name = 'product.codification.correction.line'
    _description = 'Correction codification produit line'
    _order = 'default_code,famille_id,sousfamille_id'

    name = fields.Many2one('product.product', string='Produit')
    default_code = fields.Char(related='name.default_code', string='Code')
    old_code = fields.Char('Avant')
    correction_id = fields.Many2one('product.codification.correction', string='Correction')
    famille_id = fields.Many2one(related='name.famille_id', string='Famille')
    note = fields.Char('note')
    sousfamille_id = fields.Many2one(related='name.sousfamille_id', string='SousFamille')

    def action_effacer(self):
        self.name.default_code = None
