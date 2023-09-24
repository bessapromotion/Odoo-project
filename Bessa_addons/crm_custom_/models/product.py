# -*- coding: utf-8 -*-

from odoo import models, fields, api

import json
import requests
from urllib3.exceptions import InsecureRequestWarning


class Product(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    @api.depends('superficie', 'prix_m2')
    def compute_price(self):
        for rec in self:
            rec.price_2 = rec.superficie * rec.prix_m2
            rec.list_price = rec.price_2

    @api.depends('product_variant_ids', 'name')
    def _compute_product_variant_id(self):
        for p in self:
            p.product_variant_id = p.product_variant_ids[:1].id
            p.app_id = p.product_variant_ids[:1].id

    #@api.depends('partner_ids')
    #def _nbr_partners(self):
    #    nbr = 0
     #   for rec in self:
      #      for line in rec.partner_ids:
      #              nbr += 1
       #     rec.nbr_partners = nbr
        #self.flush()

    name = fields.Char('Name', index=True, required=True, translate=True, tracking=True)
    superficie = fields.Float('Superficie', default=1, tracking=True)
    num_lot = fields.Char('N° Lot', tracking=True)
    prix_m2 = fields.Float('Prix m2', tracking=True)
    prix_m2_actuel = fields.Float('Prix Actuel m2', tracking=True)
    project_id = fields.Many2one('project.project', string='Projet', store=True, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client', readonly=1, tracking=True)
    etat = fields.Selection([('Libre', 'Libre'),
                             ('Pré-Réservé', 'Pré-Réservé'),
                             ('Réservé', 'Réservé'),
                             ('Livré', 'Livré'),
                             ('Bloqué P', 'Bloqué P'),
                             ('Bloqué C', 'Bloqué C'), ('Bloqué T', 'Bloqué T'), ('Désistement', 'Désistement'), ],
                            string='Etat du bien',
                            required=True, default='Libre',
                            tracking=True)
    order_id = fields.Many2one('sale.order', string='Devis retenu', readonly=True, tracking=True)
    bloc = fields.Char('Bloc', tracking=True)
    type_id = fields.Many2one('product.type', string='Type du bien', tracking=True)
    type_name = fields.Char(related='type_id.name', tracking=True, store=True)
    orientation = fields.Many2one('product.orientation', string='Orientation', tracking=True, default=232)
    orientation_name = fields.Char(related='orientation.name', tracking=True, store=True)
    format_id = fields.Many2one('product.format', string='Typologie', tracking=True)
    format_name = fields.Char(related='format_id.name', tracking=True, store=True)
    etage = fields.Many2one('product.etage', string='Etage', tracking=True)
    etage_name = fields.Char(related='etage.name', tracking=True, store=True)
    price_2 = fields.Float(compute=compute_price, string='Prix de vente', readonly=1, store=True)
    reservataire = fields.Char('Reservataire', tracking=True)
    manager = fields.Char('Manager', tracking=True)
    #partner_ids = fields.One2many('product.partner', 'product_id', string=u'Propriétaires')
    # products_ids = fields.One2many('product.product', 'product_tmpl_id', string='products')
    # # id_products = fields.Integer('ID BuyBessa', tracking=True, compute=get_ids)
    #nbr_partners = fields.Integer(compute=_nbr_partners, string='Nombre de propriétaires', store=True)
    product_variant_ids = fields.One2many('product.product', 'product_tmpl_id', 'Products', required=True)

    product_variant_id = fields.Many2one('product.product', 'Product', compute='_compute_product_variant_id',
                                         store=True)

    app_id = fields.Integer('ID BuyBessa', store=True)

    #@api.model
    #def create(self, vals):
    #    record = super(Product, self).create(vals)
    #    return record

    #@api.model
    #def write(self, vals):
    #    record = super(Product, self).write(vals)

     #   return record
    #@api.depends('name','etat','client_id','superficie','format_id','type_name')

    def create_synthese(self):
        print("create synthése")
        self.flush()
        self.env["product.synthesis"].search([]).unlink()
        req = "SELECT p.project_id as project,t.name as type_bien,p.format_id as typologie,count(*) as nombre, MIN(superficie) sup_minimum,MAX(superficie) sup_maximum, MIN(prix_m2) prix_m2_minimum, MAX(prix_m2) prix_m2_maximum,MIN(price_2) prix_vente_minimum,MAX(price_2) prix_vente_maximum FROM product_template as p" \
              " join product_format as f ON f.id = p.format_id" \
              " join project_project as pr ON pr.id=p.project_id" \
              " join product_type as t on t.id=p.type_id"\
              " where p.active=%s and etat='Libre' and p.sale_ok=%s " \
              " group by project,t.name,typologie" \
              " order by project "

        self._cr.execute(req, (True, True))
        all_records = self._cr.dictfetchall()
        if all_records:
            print(len (all_records))
            for record in all_records:
                print(record)
                self.env['product.synthesis'].create({
                    'project_id': record['project'],
                    'format_id': record['typologie'],
                    'sup_min': record['sup_minimum'],
                    'sup_max': record['sup_maximum'],
                    'prix_m2_min': record['prix_m2_minimum'],
                    'prix_m2_max': record['prix_m2_maximum'],
                    'prix_vente_min': record['prix_vente_minimum'],
                    'prix_vente_max': record['prix_vente_maximum'],
                    'type_bien': record['type_bien'],
                    'nombre': record['nombre'],
                })
                #self.env.cr.commit()


    @api.onchange('bloc', 'superficie', 'etage', 'etat', 'num_lot', 'format_id', 'project_id', 'orientation', 'type_id',
                  'numero')
    def change_label_2(self):
        print('change_label')
        #self.flush()
        #self.env.cr.commit()
        print('self.flush')

        if self.type_id.name == 'Appartement':
            self.name = (self.project_id.name or ' ') + ' ' + (self.type_id.name or ' ') + ' ' + (
                    self.format_id.name or ' ') + ' Bloc ' + (
                                self.bloc or '') + ' ' + (self.etage.name or ' ') + ' Lot ' + (
                                self.num_lot or ' ') + ' Sup : ' + (str(self.superficie) or ' ')
        if self.type_id.name == 'Place de parking':
            self.name = (self.project_id.name or ' ') + ' Place de parking Bloc ' + (self.bloc or '') + ' ' + (
                    self.etage.name or '') + ' Lot ' + (self.num_lot or '') + ' Num ' + (
                                self.numero or '')
        if self.type_id.name == 'Cellier':
            self.name = (self.project_id.name or ' ') + ' Cellier Bloc ' + (self.bloc or '') + ' ' + (
                    self.etage.name or '') + ' Lot ' + (self.num_lot or '') + ' Num ' + (
                                self.numero or '')
        if self.type_id.name == 'Espace a aménager':
            self.name = (self.project_id.name or ' ') + ' Espace a aménager Bloc' + (self.bloc or '') + ' ' + (
                    self.etage.name or '') + ' Lot ' + (self.num_lot or '') + ' Num ' + (
                                self.numero or '')
        if self.type_id.name == 'Local':
            self.name = (self.project_id.name or ' ') + ' Local Bloc' + (self.bloc or '') + ' ' + (
                    self.etage.name or '') + ' Lot ' + (self.num_lot or '') + ' Num ' + (
                                self.numero or '') + ' Sup : ' + str(self.superficie)
        print('end change label')
        #self.create_synthese()
# # related='product_variant_id.id',
