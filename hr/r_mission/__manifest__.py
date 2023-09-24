# -*- coding: utf-8 -*-

{
    'name': 'HR Ordre mission',
    'version': '14.0',
    'author': 'Deltalog team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Ordre de mission',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', ],
    'data': [
        'data/data.xml',
        'views/hr_view.xml',
        'views/omission_view.xml',
        'views/omission_employee_view.xml',
        'report/report_menu.xml',
        'report/report_ordre_mission.xml',
        'report/report_ordre_mission_employee.xml',
        'views/sequence.xml',
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
