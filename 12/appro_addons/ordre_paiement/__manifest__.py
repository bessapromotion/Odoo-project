# -*- coding: utf-8 -*-

{
    'name': 'Ordre de paiement',
    'version': '11.0',
    'author': 'Deltalog Team',
    'category': 'Purchase',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Ordre de paiement',
    'description': """


    """,
    'images': ['static/description/icon.png',],
    'depends': ['purchase_requisition', ],
    'data': [
            'data/data.xml',
            'security/ir.model.access.csv',
            'views/paiement_view.xml',
            'views/sequence.xml',
            'wizard/creer_paiement.xml',
            'reports/reports_menu.xml',
            'reports/ordre_paiement.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
