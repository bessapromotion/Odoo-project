# -*- coding: utf-8 -*-

from odoo import models

class ReportConcretisationXlsx(models.AbstractModel):
    _name = 'report.crm_operation_custom.report_concretisation_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        print("mmmmmmmmmmmmmmmmm")
        # for obj in partners:
        #     report_name = obj.name
        #     # One sheet by partner
        #     sheet = workbook.add_worksheet(report_name[:31])
        #     bold = workbook.add_format({'bold': True})
        #     sheet.write(0, 0, obj.name, bold)