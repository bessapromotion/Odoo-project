# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError
import time
import json
import requests
from urllib3.exceptions import InsecureRequestWarning


class SynchronisationProducts(models.TransientModel):
    _name = 'synchronisation.products.wizard'
    _description = u'Synchronisation des appartements avec Buy Bessa Par projet'

    project_id = fields.Many2one('project.project', string='Projet', store=True, tracking=True)

    def divide_chunks(self, l, n):

        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def send_all_products_per_project(self):
        print("send project products")
        req = "select pr.id as article_id,p.name,p.project_name as project,p.etage_name as etage,p.bloc as bloc,p.orientation_name as orientation,p.type_name as type,p.prix_m2,p.list_price,p.superficie,p.etat ,p.format_name as typologie from product_template p " \
              " JOIN product_product pr ON pr.product_tmpl_id=p.id " \
              " Where p.sale_ok=%s and p.project_id=%s and p.active=%s and p.type_id=%s"
        print(self.project_id)
        print(self.project_id.id)

        self._cr.execute(req, (True, self.project_id.id, True, 1))
        all_products = self._cr.dictfetchall()
        chunks = self.divide_chunks(all_products, 10)
        chunks = list(chunks)
        print('all products', len(all_products))
        print("chunks")
        if len(chunks) != 0:
            print(chunks[0], len(chunks[0]), len(chunks))
        # print("all_products")
        # print(type(all_products))
        # loop for reading chunks
        lenght = len(chunks)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        # recuperer l'URL de l'API et le token d'authentification de ir.config.parameter
        URL = self.env['ir.config_parameter'].sudo().get_param('URL', 'value')
        TOKEN = self.env['ir.config_parameter'].sudo().get_param('TOKEN', 'value')
        headers = {'content-type': 'application/json', 'Authorization': "Bearer {}".format(TOKEN)}
        i = 0
        for chunk in chunks:
            # Convertir les informations de l'appartement en JSON
            data = json.dumps(chunk)
            print(i)

            # Request
            result = requests.put(URL, data=data, headers=headers, verify=False, stream=True, timeout=30)
            i += 1
            print("r", result)
            if result.status_code == 200:
                message = ' Lenvoie des appartements a réussi. Code de réponse : ' + str(result.status_code) + str(
                    result.content) + str(len(all_products)) + '.'
            else:
                message = 'Lenvoie des appartements a  échoué. Code de réponse :' + str(result.status_code) + str(
                    result.content) + '.'
                raise UserError(_('Synchronisation error' + str(len(chunk)) + 'appartements non envoyés' + str(result.status_code) + str(
                    result.content) + '.'))
            time.sleep(5)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Succés",
                'message': 'Synchronisation établie avec succès. ' + str(
                    len(all_products)) + ' appartements envoyés' + message,
                'sticky': False,
            }
        }

    def send_all_products(self):
        print("send products")
        req = "select pr.id as article_id,p.name,p.project_name as project,p.etage_name as etage,p.bloc as bloc,p.orientation_name as orientation,p.type_name as type,p.prix_m2,p.list_price,p.superficie,p.etat ,p.format_name as typologie from product_template p " \
              " JOIN product_product pr ON pr.product_tmpl_id=p.id " \
              " Where p.sale_ok=%s  and p.active=%s and p.type_id=%s"
        self._cr.execute(req, (True, True, 1))
        all_products = self._cr.dictfetchall()
        chunks = self.divide_chunks(all_products, 10)
        chunks = list(chunks)
        print('all products', len(all_products))
        print("chunks")
        if len(chunks) != 0:
            print(chunks[0], len(chunks[0]), len(chunks))
        # print("all_products")
        # print(type(all_products))
        # loop for reading chunks
        lenght = len(chunks)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        # recuperer l'URL de l'API et le token d'authentification de ir.config.parameter
        URL = self.env['ir.config_parameter'].sudo().get_param('URL', 'value')
        TOKEN = self.env['ir.config_parameter'].sudo().get_param('TOKEN', 'value')
        headers = {'content-type': 'application/json', 'Authorization': "Bearer {}".format(TOKEN)}
        i = 0
        for chunk in chunks:
            # Convertir les informations de l'appartement en JSON
            data = json.dumps(chunk)
            print(i)

            # Request
            result = requests.put(URL, data=data, headers=headers, verify=False, stream=True, timeout=30)
            i += 1
            print("r", result)
            if result.status_code == 200:
                message = ' Lenvoie des appartements a réussi. Code de réponse : ' + str(result.status_code) + str(
                    result.content) + str(len(all_products)) + '.'
            else:
                message = 'Lenvoie des appartements a  échoué. Code de réponse :' + str(result.status_code) + str(
                    result.content) + '.'
                raise UserError(_('Synchronisation error' + str(len(chunk)) + 'appartements non envoyés'))
            time.sleep(5)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Succés",
                'message': 'Synchronisation établie avec succès. ' + str(
                    len(all_products)) + ' appartements envoyés' + message,
                'sticky': False,
            }
        }
    
    def synchroniser_projet(self, project_id):
        print("send project products")
        req = "select pr.id as article_id,p.name,p.project_name as project,p.etage_name as etage,p.bloc as bloc,p.orientation_name as orientation,p.type_name as type,p.prix_m2,p.list_price,p.superficie,p.etat ,p.format_name as typologie from product_template p " \
              " JOIN product_product pr ON pr.product_tmpl_id=p.id " \
              " Where p.sale_ok=%s and p.project_id=%s and p.active=%s and p.type_id=%s"
        print(self.project_id)
        print(project_id)
        print(self.project_id.id)
        self._cr.execute(req, (True, project_id, True, 1))
        all_products = self._cr.dictfetchall()
        chunks = self.divide_chunks(all_products, 10)
        chunks = list(chunks)
        print(' synchroniser_projet all products ', len(all_products))
        print("chunks")
        if len(chunks) != 0:
            print(chunks[0], len(chunks[0]), len(chunks))
        lenght = len(chunks)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        # recuperer l'URL de l'API et le token d'authentification de ir.config.parameter
        URL = self.env['ir.config_parameter'].sudo().get_param('URL', 'value')
        TOKEN = self.env['ir.config_parameter'].sudo().get_param('TOKEN', 'value')
        headers = {'content-type': 'application/json', 'Authorization': "Bearer {}".format(TOKEN)}
        i = 0
        for chunk in chunks:
            # Convertir les informations de l'appartement en JSON
            data = json.dumps(chunk)
            print(i)

            # Request
            result = requests.put(URL, data=data, headers=headers, verify=False, stream=True, timeout=30)
            i += 1
            print("r", result)
            print("r", result.content)
            if result.status_code == 200:
                message = ' Lenvoie des appartements a réussi. Code de réponse : ' + str(result.status_code) + str(
                    result.content) + str(len(all_products)) + '.'
            else:
                message = 'Lenvoie des appartements a  échoué. Code de réponse :' + str(result.status_code) + str(
                    result.content) + '.'
                raise UserError(_('Synchronisation error' + str(len(chunk)) + 'appartements non envoyés'))
            time.sleep(5)
        print("Projet with id ", project_id, "Synchronized Successfully")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': "Succés",
                'message': 'Synchronisation établie avec succès. ' + str(
                    len(all_products)) + ' appartements envoyés' + message,
                'sticky': False,
            }
        }

    def create_records(self):
        print("send project products")
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
                self.env.cr.commit()
