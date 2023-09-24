# -*- coding: utf-8 -*-

{
    'name': 'HR Affectation',
    'version': '15.0.1',
    'author': 'Deltalog team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Affectation',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'project', 'hr_dynamic_reports'],
    'data': [
        'data/data.xml',
        'report/affectation_report_view.xml',
        'report/report_menu.xml',
        'views/affectation_view.xml',
        'views/hr_direction.xml',
        'views/hr_department.xml',
        'views/hr_view.xml',
        'security/ir.model.access.csv',
        'security/rule.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
