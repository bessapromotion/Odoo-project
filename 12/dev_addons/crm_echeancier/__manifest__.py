# -*- coding: utf-8 -*-

{
    'name': 'Echeancier',
    'version': '12.0',
    'author': 'Deltalog team',
    'category': 'CRM',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Echeancier',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['account', 'crm_operation', 'sale_management'],
    'data': [
        'security/crm_echeancier_security.xml',
        'security/ir.model.access.csv',
        'views/sequences.xml',
        'wizard/creer_echeancier.xml',
        'wizard/creer_echeancier_tva.xml',
        'wizard/creer_paiement.xml',
        'wizard/change_amount.xml',
        'report/ordre_paiement.xml',
        'wizard/print_ordre_paiement.xml',
        'report/reports_menu.xml',
        'report/recu_paiement.xml',
        'report/reservation.xml',
        'views/echeancier_view.xml',
        'views/echeancier_modele_view.xml',
        'views/payment_view.xml',
        'views/order_view.xml',
        'views/invoice_view.xml',
        'views/ordre_paiement_view.xml',
        'views/partner_view.xml',
        'views/reservation_view.xml',
        'views/annulation_view.xml',
        'views/project_view.xml',
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
