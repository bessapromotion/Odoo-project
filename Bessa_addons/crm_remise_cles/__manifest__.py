# -*- coding: utf-8 -*-

{
    'name': 'Remise des clés',
    'version': '15.0',
    'author': 'OMARI Rahma Nour elhouda',
    'license': 'LGPL-3',
    'category': 'CRM',
    'sequence': 1,
    'summary': ' - Remise des clés : - suivre les remises des clés '
               '                    - suivre les décicions daffectation '
               ' - Suivre les changement de propriétaire',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['base', 'mail', 'crm_product', 'account', 'sale', 'crm_operation', 'crm_echeancier', 'hr_base', 'crm_custom'],
    'data': [
        'security/ir.model.access.csv',
        'reports/pv_appartement.xml',
        'reports/pv_cellier.xml',
        'reports/cahier_charge.xml',
        'reports/decision_affectation.xml',
        'reports/decision_affectation_credit.xml',
        'reports/reports_menu.xml',
        'views/remise_cles_view.xml',
        'views/article_view.xml',
        #'views/order_view.xml',
        #'views/product_partner_view.xml',
        #'views/product_template_view.xml',
        'views/decision_affectation_view.xml',
        #'views/changement_proprietaire_view.xml',
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
