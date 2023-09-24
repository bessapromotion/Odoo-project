# -*- coding: utf-8 -*-

{
    'name': 'TdB Opérations',
    'version': '15.0',
    'author': 'Deltalog team',
    'license': 'LGPL-3',
    'category': 'CRM',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Tableaux de bord des Opérations',
    'description': """
    
    
    """,
    'images': [],
    'depends': ['crm_operation', 'crm_echeancier', 'sale', 'crm_product'],
    'data': [
        'security/ir.model.access.csv',
        'security/tdb_security.xml',
        'data/config.xml',
        'views/sale_view.xml',
        'views/echeancier_view.xml',
        'views/reservation_view.xml',
        'views/project_view.xml',
        'views/stock_vente_tdb.xml',
        'views/recouvrement_tdb.xml',
        'views/segmentation_tdb.xml',
        'views/res_users.xml',

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
