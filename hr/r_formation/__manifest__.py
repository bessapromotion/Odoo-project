# -*- coding: utf-8 -*-

{
    'name': 'HR Formation',
    'version': '14.0e',
    'author': 'Deltalog Team',
    'license': 'LGPL-3',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'Gestion de la formation',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/partner_view.xml',
        'views/theme_view.xml',
        'views/besoin_view.xml',
        'views/demande_view.xml',
        'views/evaluation_view.xml',
        'views/session_gantt.xml',
        'views/session_view.xml',
        'views/formation_gantt.xml',
        'views/plan_view.xml',
        'views/analyse.xml',
        'views/sequence.xml',
        'views/historique.xml',
        'views/menu_view.xml',
        'wizard/wiz_motif_view.xml',

        'report/report_fiche_presence.xml',
        'report/report_besoin_formation.xml',
        'report/report_menu.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
