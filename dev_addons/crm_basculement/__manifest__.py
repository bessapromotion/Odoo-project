# -*- coding: utf-8 -*-

{
    'name': 'Basculement',
    'version': '15.0',
    'author': 'Deltalog team',
    'category': 'CRM',
    'license': 'LGPL-3',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Suivre les dossiers des clients',
    'description': """
    
    - Basculement
    
    """,
    'images': ['static/description/icon.png', ],
    'depends': ['crm_operation', 'crm_echeancier'],
    'data': [
        'security/ir.model.access.csv',
        'views/sequences.xml',

        'views/basculement_view.xml',
        'views/menu_view.xml',
        'report/basculement.xml',
        'report/reports_menu.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
