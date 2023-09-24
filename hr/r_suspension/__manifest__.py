# -*- coding: utf-8 -*-

{
    'name': 'HR Suspension',
    'version': '14.0e',
    'author': 'Deltalog team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Suspension',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'r_sanction', 'r_questionnaire', ],
    'data': [
            # 'data/data.xml',
            'report/report_menu.xml',
            'report/report_decision_suspension.xml',
            'views/suspension_view.xml',
            # 'views/parametre_view.xml',
            'views/sequence.xml',
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
