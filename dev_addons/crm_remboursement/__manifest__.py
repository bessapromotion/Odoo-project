# -*- coding: utf-8 -*-

{
    'name': 'Suivi du remboursement',
    'version': '15.0',
    'author': 'Deltalog team',
    'license': 'LGPL-3',
    'category': 'CRM',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Suivre les dossiers de remboursement',
    'description': """
     
    """,
    'images': ['static/description/icon.png', ],
    'depends': ['crm_echeancier'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'security/rule.xml',
        'wizard/creer_paiement.xml',
        'views/annulation_view.xml',
        'views/remboursement_view.xml',
        'views/payment_view.xml',
        'views/menu_view.xml',

    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
