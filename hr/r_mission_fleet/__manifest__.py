# -*- coding: utf-8 -*-

{
    'name': 'HR Ordre mission - fleet',
    'version': '14.0',
    'author': 'Deltalog team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Ordre de mission - fleet',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['r_mission', 'fleet'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/omission_view.xml',
        'wizard/wiz_depart_view.xml',
        'wizard/wiz_arrivee_view.xml',
        'wizard/wiz_autorisation_view.xml',
        'report/layouts.xml',
        'report/report_autorisation.xml',
        # 'report/report_mission.xml',
        # 'report/report_menu.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
