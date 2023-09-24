# -*- coding: utf-8 -*-

{
    'name': 'Purchase Reports',
    'version': '12.0',
    'author': 'Deltalog Team',
    'category': 'Purchase',
    'sequence': 1,
    'website': 'http://www.deltalog.com',
    'summary': 'Purchase Reports',
    'description': """

    """,
    'images': ['static/description/icon.png',],
    'depends': ['purchase', 'project', 'ordre_paiement'],
    'data': [
            'views/purchase_view.xml',
            'reports/purchase_report.xml',
            'reports/purchase_quotation_report.xml',
            'reports/external_layouts.xml',

            ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
