# -*- coding: utf-8 -*-

{
    'name': 'HR Contrat',
    'version': '13.0',
    'author': 'Deltalog Team',
    'category': 'Human Resources',
    'sequence': 1,
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'hr_contract', 'hr_company'],
    'data': [
        'data/data.xml',
        'views/sequence.xml',
        'views/contrat_view.xml',
        'views/type_contrat_view.xml',
        'views/article_view.xml',
        'views/modele_view.xml',
        'views/contract_parametre.xml',
        'views/employe.xml',
        'security/ir.model.access.csv',
        'report/report_contrat_cdd.xml',
        'report/report_contrat_cdi.xml',
        'report/report_accord_confidentialite.xml',
        'report/repport_annonce_recrutement.xml',
        'report/report_menu.xml',
    ],

    'demo': [],
    'test': [],

    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
