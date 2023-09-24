# -*- coding: utf-8 -*-

{
    'name': 'Algeria - Fiscal Timbre For Purchase ',
    'version': '15.0',
    'category': 'Localization',
    'description': """
This is the module to manage the Fiscal Timbre in Odoo.
========================================================================

This module applies to companies based in Algeria.

""",
    'author': 'DELTALOG TEAM',
    'website': 'http://www.deltalog.dz/',
    'depends': ['purchase', 'purchase_reports'],
    'data': [
        'data/timbre_data.xml',
        'security/ir.model.access.csv',
        'views/timbre_view.xml',
        'views/purchase_invoice_view.xml',
        'views/account_view.xml',
        'reports/purchase_report.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
