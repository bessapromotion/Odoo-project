# -*- coding: utf-8 -*-

{
    'name': u'Dépenses',
    'version': '15.0',
    'author': 'Omari Rahma Nourelhouda',
    'license': 'LGPL-3',
    'category': 'CRM',
    'sequence': 1,
    'summary': ' 1 - Journal des recettes et dépenses  ',

    'description': """

    - Journal des dépenses
    - la caisse des dépense.
    - Journal des recettes
    - la caisse des recettes.

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['base', 'hr_base', 'hr', 'gestion_profil', 'account','crm_echeancier'],
    'data': [
        # 'data/data.xml',
        'security/crm_depenses_security.xml',
        'security/ir.model.access.csv',
        'reports/fiche_depense.xml',
        'reports/fiche_mouvement.xml',
        'reports/recu_paiement_classique.xml',
	'reports/fiche_operation_bancaire.xml',
	'reports/recu_paiement_charge.xml',
        'reports/reports_menu.xml',
        'views/company_account_view.xml',
        'views/company_view.xml',
        'views/depense_month_view.xml',
        'views/depense_nature_view.xml',
        'views/depense_projet_view.xml',
        'views/depense_type_view.xml',
        'views/depense_type_benificiaire_view.xml',
        'views/depense_week_view.xml',
        'views/depense_tag_view.xml',
        'views/depense_view.xml',
        'views/operation_bancaire_view.xml',
        'views/menu_view.xml',
        # 'views/caisse_bill_view.xml',
        # 'views/menu_view.xml',
        # 'report/annulation_report.xml',
        # 'report/concretisation_report.xml',
        # 'report/report_cloture_caisse.xml',
        # 'report/report_pv_caisse.xml',
        # 'report/report_pv_coffre.xml',
        # 'report/reports_menu.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
