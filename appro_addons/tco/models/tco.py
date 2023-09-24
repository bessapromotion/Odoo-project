# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Requisition(models.Model):
    _name    = 'purchase.requisition'
    _inherit    = 'purchase.requisition'

    tco_ids = fields.One2many('tco.line', 'reqisition_id', string='Consultation', readonly=1)
    # order_id = fields.Many2one('purchase.order', string='Fournisseur sélectionné')
    orders_ids = fields.One2many(related='purchase_ids', readonly=1)
    commission_ids = fields.One2many('tco.commission', 'reqisition_id', string='Commission', states={'done': [('readonly', True)]})
    commission_date = fields.Date('Date commission', states={'done': [('readonly', True)]})
    commission_decision = fields.Text(u'Décision', states={'done': [('readonly', True)]})

    def print_tco(self):
        return self.env.ref('tco.act_report_tco').report_action(self)

    # @api.one
    def action_generate_tco(self):
        i = 0
        self.tco_ids.unlink()
        for product in self.line_ids:
            i += 1
            self.env['tco.line'].create({
                'name'          : i,
                'product_id'    : product.product_id.id,
                'reqisition_id': self.id,
            })

        order_list = self.env['purchase.order'].search([('requisition_id', '=', self.id), ('state', 'not in', ('cancel',))])
        if order_list.exists():
            i = 0
            for order in order_list:
                i += 1
                for rec in order.order_line:

                    cell = self.env['tco.cell'].create({
                        'name'        : str(rec.product_qty) + ' X ' + str(rec.price_unit) + ' ' + order.currency_id.name,
                        'product_id'  : rec.product_id.id,
                        'product_qty' : rec.product_qty,
                        'price_unit'  : rec.price_unit,
                        'amount'      : rec.product_qty * rec.price_unit,
                        'visible'     : True,
                        'order_id'    : order.id,
                    })
                    line = self.env['tco.line'].search([  # ('order_id', '=', rec.id),
                                                        ('product_id', '=', rec.product_id.id),
                                                        ('reqisition_id', '=', self.id)])
                    if line.exists():
                        line.write({'order_'+str(i): cell.id})


class TcoCell(models.Model):
    _name    = 'tco.cell'
    _description = 'Ligne TCO'

    name        = fields.Char('Designation')
    product_id  = fields.Many2one('product.product', string='Produit')
    company_id = fields.Many2one('res.company', string=u'Société',
                                 default=lambda self: self.env['res.company']._company_default_get('account.move'))
    currency_id = fields.Many2one(related='company_id.currency_id', string='Devise', readonly=1)

    product_qty = fields.Float('Quantité')
    price_unit  = fields.Monetary('Prix unitaire')
    amount      = fields.Monetary('Montant HT')
    visible     = fields.Boolean('Visible')
    order_id    = fields.Many2one('purchase.order', string='Devis Fournisseur')


class TcoLine(models.Model):
    _name    = 'tco.line'
    _description = 'Ligne TCO'

    # @api.one
    # def _default_currency(self):
    #     return self.env['res.company'].browse(1).currency_id.id

    name       = fields.Char('#')
    reqisition_id = fields.Many2one('purchase.requisition')
    product_id = fields.Many2one('product.product', string='Produit')
    company_id = fields.Many2one('res.company', string=u'Société',
                                 default=lambda self: self.env['res.company']._company_default_get('account.move'))
    currency_id = fields.Many2one(related='company_id.currency_id', string='Devise', readonly=1)

    order_1    = fields.Many2one('tco.cell', string='Fournisseur 1')
    qty_1   = fields.Float(related='order_1.product_qty', currency_field='currency_id', string='.')
    pu_1   = fields.Monetary(related='order_1.price_unit', currency_field='currency_id', string='Fournissseur 1')
    amount_1   = fields.Monetary(related='order_1.amount', currency_field='currency_id', string='.')
    sep_1   = fields.Char(string='|', default='   |   ')
    order_2    = fields.Many2one('tco.cell', string='Fournisseur 2')
    qty_2 = fields.Float(related='order_2.product_qty', currency_field='currency_id', string='.')
    pu_2 = fields.Monetary(related='order_2.price_unit', currency_field='currency_id', string='Fournissseur 2')
    amount_2   = fields.Monetary(related='order_2.amount', currency_field='currency_id', string='.')
    sep_2 = fields.Char(string='|', default='   |   ')

    order_3    = fields.Many2one('tco.cell', string='Fournisseur 3')
    qty_3 = fields.Float(related='order_3.product_qty', currency_field='currency_id', string='.')
    pu_3 = fields.Monetary(related='order_3.price_unit', currency_field='currency_id', string='Fournissseur 3')
    amount_3   = fields.Monetary(related='order_3.amount', currency_field='currency_id', string='.')


class TcoCommission(models.Model):
    _name = 'tco.commission'
    _description = 'Commission'

    name = fields.Many2one('hr.employee', string='Membre commission')
    job_id = fields.Many2one(related='name.job_id', string='Fonction', readonly=1)
    reqisition_id = fields.Many2one('purchase.requisition')

