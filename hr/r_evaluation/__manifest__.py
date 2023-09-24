# -*- coding: utf-8 -*-

{
    'name': 'HR Evaluation',
    'version': '13.0e',
    'author': 'Deltalog team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Evaluation individuelle',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base'],
    'data': [
            'data/criters_data.xml',
            'report/reports_menu.xml',
            'report/report_fiche_evaluation_individuelle.xml',
            'views/evaluation_view.xml',
            'views/evaluation_criters.xml',
            'views/job_view.xml',
            'views/sequence.xml',
            'wizard/create_evaluation_view.xml',
            'security/security.xml',
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
