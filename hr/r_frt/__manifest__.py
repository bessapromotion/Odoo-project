# -*- coding: utf-8 -*-

{
    'name': 'HR FRT',
    'version': '14.0e',
    'author': 'Deltalog Team',
    'licence': 'LGPL-3',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Fin relation de travail',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['r_preavis_fin_contrat', 'r_demission', 'r_mise_en_demeure', 'r_evaluation', 'r_contract',
                'hr_dynamic_reports'],
    'data': [
        'report/report_annonce_depart.xml',
        'report/report_quitus.xml',
        'report/report_decision_fin_relation_travail.xml',
        'report/reports_menu.xml',
        'views/frt_view.xml',
        'views/parametre_view.xml',
        'views/menu_view.xml',
        'data/data.xml',
        'views/demission.xml',
        'views/sequence.xml',
        'security/rule.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
