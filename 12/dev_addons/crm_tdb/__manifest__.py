# -*- coding: utf-8 -*-

{
    'name': 'TdB Opérations',
    'version': '12.0',
    'author': 'Deltalog team',
    'category': 'CRM',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Tableaux de bord des Opérations',
    'description': """
    
    
    """,
    'images': [ ],
    'depends': ['crm_operation', 'crm_echeancier'],
    'data': [

        'views/sale_view.xml',
        'views/echeancier_view.xml',
        'views/reservation_view.xml',

        'views/menu_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
