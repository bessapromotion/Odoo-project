# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class ConcretisationReportWizard(models.TransientModel):
    _name = 'concretisation.report.wizard'
    _description = u'Générer le rapport des concretisations'

    type = fields.Selection([('day', 'Journalier'), ('period', u'Périodique')], default='day')
    date_start = fields.Date(u'Date de début')
    date_end = fields.Date(u'Date de fin')

    def action_print_pdf_report(self):
        domain1 = []
        domain2 = []
        date_start = self.date_start
        date_end = self.date_start
        type = self.type
        if type == 'day':
            domain1 += [('validity_date', '=', date_start)]
            Concretisation = self.env['sale.order'].search(domain1)
        else:
            if date_start and date_end:
                domain2 += [('validity_date', '>=', date_start)]
                domain2 += [('validity_date', '<=', date_end)]
            Concretisation = self.env['sale.order'].search(domain2)
        Concretisation_list = []
        for order in Concretisation:
            req = "SELECT p.name,l.price_unit from sale_order as s " \
                  " Join sale_order_line as l ON s.id=l.order_id " \
                  " JOIN product_product as pr ON pr.id=l.product_id " \
                  " JOIN product_template as p on p.id=pr.product_tmpl_id" \
                  " where  s.id=%s and p.sale_ok=%s "
            id = order.id
            self._cr.execute(req, (id, True))
            appartement = self._cr.dictfetchone()
            print(appartement)
            vals = {
                'ref': order.name,
                'client': order.partner_id.name,
                'date_concretisation': order.validity_date,
                'projet': order.project_id.name,
                'Appartement': appartement['name'],
                'Num_dossier': order.num_dossier,
                'type_bien': order.type_bien,
                'commercial': order.user_id.name,
                'company': order.company_id,
                'Total_paiement': order.total_paiement,
                'Total_HT': appartement['price_unit']

            }
            print("before")
            Concretisation_list.append(vals)
        data = {
            'form_data': self.read()[0],
            'concretisations': Concretisation_list
        }
        return self.env.ref('crm_cloture_caisse.action_report_concretisation_xml').report_action(self, data=data)
