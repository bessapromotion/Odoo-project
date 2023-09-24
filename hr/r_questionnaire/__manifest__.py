# -*- coding: utf-8 -*-

{
    'name': 'HR Questionaire disciplinaire',
    'version': '14.0e',
    'author': 'Deltalog team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Questionnaire disciplinaire',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'r_contract'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'security/rule.xml',
        'views/questionnaire_view.xml',
        # 'views/parametre_view.xml',
        'views/sequence.xml',
        'report/report_menu.xml',
        'report/report_questionnaire_vide.xml',
        'report/report_questionnaire.xml',

    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
