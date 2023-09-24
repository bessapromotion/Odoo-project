# -*- coding: utf-8 -*-

{
    'name': 'TCO',
    'version': '11.0',
    'author': 'Deltalog Team',
    'category': 'Purchase',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Tableau comparatif des offres',
    'description': """


    """,
    'images': ['static/description/icon.png',],
    'depends': ['purchase_requisition', 'hr', ],
    'data': [
            'security/ir.model.access.csv',
            'views/tco_view.xml',
            'reports/reports_menu.xml',
            'reports/tco.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
