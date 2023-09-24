# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductType(models.Model):
    _name = 'product.type'
    _description = 'Type'

    name = fields.Char('Type')


class ProductFormat(models.Model):
    _name = 'product.format'
    _description = 'Format'

    name = fields.Char('Type', help='F3, F4, F5...')


class ProductOrientation(models.Model):
    _name = 'product.orientation'
    _description = 'Orientation'

    name = fields.Char('Orientation')


class ProductEtage(models.Model):
    _name = 'product.etage'
    _description = 'Etage'

    name = fields.Char('Etage')


class Product(models.Model):
    _name    = 'product.template'
    _inherit = 'product.template'

    @api.one
    @api.depends('superficie', 'prix_m2')
    def compute_price(self):
        for rec in self:
            rec.price_2 = rec.superficie * rec.prix_m2

    bloc               = fields.Char('Bloc')
    type_id            = fields.Many2one('product.type', string='Type du bien')
    orientation        = fields.Many2one('product.orientation', string='Orientation')
    format_id          = fields.Many2one('product.format', string='Typologie')
    etage              = fields.Many2one('product.etage', string='Etage')
    niveau             = fields.Float('Niveau', default=0.0)
    numero             = fields.Char(u'Numéro')
    superficie         = fields.Float('Superficie', default=1)
    surf_habitable_edd = fields.Float('Surface habitable(EDD)')
    surf_utile_edd     = fields.Float('Surface utile(EDD)')
    surf_habitable_com = fields.Float('Surface habitable(COM)')
    surf_utile_com     = fields.Float(related='superficie', string='Surface utile(COM)')
    num_lot            = fields.Char('N° Lot')
    prix_m2            = fields.Float('Prix m2')
    prix_m2_actuel     = fields.Float('Prix Actuel m2')
    project_id         = fields.Many2one('project.project', string='Projet')
    # price_2          = fields.Float(related='list_price', string='Prix de vente', readonly=1)
    price_2            = fields.Float(compute=compute_price, string='Prix de vente', readonly=1)
    client_id          = fields.Many2one('res.partner', string='Client', readonly=1)
    etat               = fields.Selection([('Libre', 'Libre'),
                                     ('Pré-Réservé', 'Pré-Réservé'),
                                     ('Réservé', 'Réservé'),
                                     ('Livré', 'Livré'),
                                     ('Bloqué P', 'Bloqué P'),
                                     ('Bloqué C', 'Bloqué C'), ], string='Etat du bien')
    order_id       = fields.Many2one('sale.order', string='Devis retenu', readonly=True)
    plan_pdf       = fields.Binary('Plan')
    plan_1_pdf     = fields.Binary(related='plan_pdf', string='Plan', readonly=True)

    # reservation_id = fields.Many2one('crm.reservation', string='Réservation', readonly=True)
    line_ids       = fields.One2many('sale.order.line', 'product_tmpl_id2', string='Pré-réservation en cours', domain=[('state', '!=', 'cancel')])
    line_canceled_ids = fields.One2many('sale.order.line', 'product_tmpl_id2', string='Pré-réservation annulée', domain=[('state', '=', 'cancel')])
    view_orders    = fields.Boolean('Afficher le detail', default=False)


class ProductProduct(models.Model):
    _name    = 'product.product'
    _inherit = 'product.product'

    line_ids = fields.One2many('sale.order.line', 'product_id', string='Pré-réservation en cours', domain=[('state', '!=', 'cancel')])
