# -*- coding: utf-8 -*-

{
    'name': 'Cloture de caisse',
    'version': '15.0',
    'author': 'Omari Rahma Nourelhouda',
    'license': 'LGPL-3',
    'category': 'CRM',
    'sequence': 1,
    'summary': ' 1 - Generer des rapports journaliers ou periodiques des concrétisation, annulations                                                                                                                                       '
               ' 2 - Ouverture et cloture de caisse'
               ' 3- Impression de pv de recettes de caisse ',

    'description': """
    
    - Pré-réservations
    - Réservation
    - Désistement
    - Basculement
    
    """,
    'images': ['static/description/icon.png', ],
    'depends': ['base', 'mail', 'crm_product', 'account', 'crm_operation', 'crm_remboursement', 'report_xlsx','crm_custom','crm_depenses', 'gestion_profil'],
    'data': [
        # 'data/data.xml',
        'security/crm_operation_custom_security.xml',
        'security/rule.xml',
        'security/ir.model.access.csv',
        'wizard/concretisation_report_view.xml',
        'wizard/annulation_report_view.xml',
        'wizard/open_caisse_view.xml',
        'views/caisse_view.xml',
        'views/bill_view.xml',
        # 'views/payment_depense_view.xml',
        'views/caisse_bill_view.xml',
        'views/menu_view.xml',
        'report/annulation_report.xml',
        'report/concretisation_report.xml',
        'report/report_cloture_caisse.xml',
        'report/report_pv_caisse.xml',
        'report/report_pv_coffre.xml',
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
