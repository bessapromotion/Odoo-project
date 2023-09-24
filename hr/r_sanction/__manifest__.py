# -*- coding: utf-8 -*-

{
    'name': 'HR Décision disciplinaire',
    'version': '14.0e',
    'author': 'Deltalog team',
    'category': 'hr',
    'license': 'LGPL-3',
    'sequence': 1,
    'website': '',
    'summary': 'HR Décision disciplinaire',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['base', 'mail', 'hr_base', 'r_contract', 'r_questionnaire', 'hr_dynamic_reports'],
    'data': [
        'security/ir.model.access.csv',
        'security/rule.xml',
        'views/sanction_view.xml',
        'report/report_menu.xml',
        'report/report_decision_sanction.xml',
        'views/sanction_view.xml',
        'views/parametre_view.xml',
        'views/sequence.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
