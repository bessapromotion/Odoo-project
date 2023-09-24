# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class AnnulationReportWizard(models.TransientModel):
    _name = 'annulation.report.wizard'
    _description = u'Générer le rapport des annulations'

    type = fields.Selection([('day', 'Journalier'), ('period', u'Périodique')], default='day')
    date_start = fields.Date(u'Date de début')
    date_end = fields.Date(u'Date de fin')

    def action_print_pdf_report(self):
        domain1=[]
        domain2 =[]
        date_start = self.date_start
        date_end = self.date_start
        type= self.type
        if type == 'day' :
            if date_start :
               domain1 += [('date','=',date_start)]
            annulations1 = self.env['crm.annulation'].search(domain1)
            annulation1_list = []
            for ann in annulations1 :
                total_paye =0
                for ech in ann.echeancier_ids:
                    total_paye += ech.montant
                vals={
                    'ref' : ann.name,
                    'client': ann.partner_id.name,
                    'date_reservation': ann.date_reservation,
                    'projet': ann.project_id.name,
                    'Appartement' : ann.product_ids.name.name,
                    'Total_paye' : total_paye
                }
                annulation1_list.append(vals)
            data = {
                'form_data': self.read()[0],
                'annulations': annulation1_list
            }
        else:
                if date_start and date_end:
                    domain2 += [('date', '>=', date_start)]
                    domain2 += [('date', '<=', date_end)]

                annulations2 = self.env['crm.annulation'].search(domain2)
                annulations2_list = []
                for ann in annulations2:
                    total_paye = 0
                    for ech in ann.echeancier_ids:
                        total_paye += ech.montant
                    vals = {
                        'ref': ann.name,
                        'client': ann.partner_id.name,
                        'date_reservation': ann.date_reservation,
                        'projet': ann.project_id.name,
                        'Appartement': ann.product_ids.name.name,
                        'Total_paye': total_paye
                    }
                    annulations2_list.append(vals)
                data = {
                        'form_data' : self.read()[0],
                        'annulations': annulations2_list
                    }
        return self.env.ref('crm_cloture_caisse.action_report_annulation_xml').report_action(self, data=data)



