# -*- coding: utf-8 -*-

{
    'name': 'Personalisation des modules DL',
    'version': '15.0',
    'author': 'Omari Rahma Nourelhouda',
    'license': 'LGPL-3',
    'sequence': 1,
    'website': '',
    'summary': 'Amélioration des modules Deltalog',
    'description': """


    """,
    'images': ['static/description/icon.png', ],
    'depends': ['base', 'product', 'crm_product', 'crm_operation', 'crm_basculement' ,'crm_echeancier',
                'crm_remboursement', 'gestion_profil',
                'crm_visite', 'account', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/send_all_product_schedule.xml',
        'views/payment_view.xml',
	#'views/product_partner_view.xml',
        'views/echeancier_view.xml',
        'wizard/creer_echeancier_tva.xml',
        'wizard/synchronisation_products.xml',
        #'wizard/creer_paiement.xml',
         'wizard/calcul_remise_pourcentage.xml',
        'views/product_synthesis_view.xml',
        'views/order_view.xml',
        'views/crm_reservation.xml',
        'views/product_view.xml',
        'views/partner_view.xml',
        'views/basculement_view.xml',
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
