# -*- coding: utf-8 -*-

{
    'name': 'Suivi des dossiers',
    'version': '12.0',
    'author': 'Deltalog team',
    'category': 'CRM',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Suivre les dossiers des clients',
    'description': """
    
    - Pré-réservations
    - Réservation
    - Désistement
    - Basculement
    
    """,
    'images': ['static/description/icon.png', ],
    'depends': ['base', 'mail', 'crm_product'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/sequences.xml',

        'config/configuration.xml',
        'views/reservation_view.xml',
        'views/annulation_view.xml',
        # 'views/basculement_view.xml',
        'views/prereservation_view.xml',
        'views/order_view.xml',
        # 'views/invoice_view.xml',
        'views/order_menu_view.xml',
        'views/configuration_view.xml',
        'views/menu_view.xml',
        'report/reports_menu.xml',
        'report/annulation.xml',
        'report/reservation.xml',
        # 'report/basculement.xml',
        'views/product_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
