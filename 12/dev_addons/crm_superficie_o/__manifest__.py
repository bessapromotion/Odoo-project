# -*- coding: utf-8 -*-

{
    'name': 'Changements surfaciques',
    'version': '12.0',
    'author': 'Deltalog team',
    'category': 'CRM',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Changement de superficie',
    'description': """
    
    """,
    'images': ['static/description/icon.png', ],
    'depends': ['crm_operation', 'crm_echeancier', 'crm_remboursement'],
    'data': [
        'security/superficie_security.xml',
        'security/ir.model.access.csv',
        'views/sequences.xml',
        'wizard/charger_bien.xml',
        'views/superficie_view.xml',
        'views/product_view.xml',
        'views/order_view.xml',
        'views/echeancier_view.xml',
        'views/remboursement_view.xml',

        'views/menu_view.xml',
        # 'report/basculement.xml',
        # 'report/reports_menu.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
