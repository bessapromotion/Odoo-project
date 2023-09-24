# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import date


class ProductSynthesis(models.Model):
    _name = 'product.synthesis'
    _description = " synthése des produits"



    project_id = fields.Many2one('project.project', string='Projet',stored=True)
    format_id = fields.Many2one('product.format', string='Typologie', store=True)
    product_ids = fields.Many2one('product.template', string='Biens',
                                  domain=[('project_id', '=', project_id), ('etat', '=', 'Libre'),('format_id', '=', format_id)])
    type_bien = fields.Char( string='Type du bien')
    sup_min = fields.Float('Superficie minimum')
    sup_max = fields.Float('Superficie maximum')
    prix_m2_min = fields.Float('Prix m2 minimum')
    prix_m2_max = fields.Float('Prix m2 maximum')
    prix_vente_min = fields.Float('Prix de vente minimum')
    prix_vente_max = fields.Float('Prix de vente maximum')
    nombre = fields.Integer('Nombre')



    @api.depends('project_id','product_ids','format_id')
    def create_records(self):
        print("send project products")
        self.env["product.synthesis"].search([]).unlink()
        req = "SELECT pr.name as project,t.name as type_bien,p.format_id as typologie,count(*) as nombre, MIN(superficie) sup_minimum,MAX(superficie) sup_maximum, MIN(prix_m2) prix_m2_minimum, MAX(prix_m2) prix_m2_maximum,MIN(price_2) prix_vente_minimum,MAX(price_2) prix_vente_minimum FROM product_template as p"\
            "join product_format as f ON f.id = p.format_id"\
            "join project_project as pr ON pr.id=p.project_id" \
            "where p.active=%s and etat='Libre' and p.sale_ok=%s " \
            "group by project,t.name,typologie" \
            "order by project "

        self._cr.execute(req, (True, 1, True))
        all_records = self._cr.dictfetchall()
        if all_records:
            for record in all_records:
                self.env['product.synthesis'].create({
                    'project_id': record['project'],
                    'format_id': record['typologie'],
                  'sup_min': record['sup_minimum'],
                  'sup_max': record['sup_maximum'],
                    'prix_m2_min': record['prix_m2_minimum'],
                    'prix_m2_max': record['prix_m2_maximum'],
                    'prix_vente_min': record['prix_vente_minimum'],
                    'prix_vente_max': record['prix_vente_maximum'],
                    'type_bien' : record['type_bien'],
                    'nombre' : record['nombre'],
                })
                self.env.cr.commit()




