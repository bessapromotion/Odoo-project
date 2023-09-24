# -*- coding: utf-8 -*-

{
    'name': 'HR Promotion',
    'version': '10.0.0.1',
    'author': 'Lunar Tech',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Promotion',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'hr_dynamic_reports'],
    'data': [
        'report/report_menu.xml',
        'report/report_promotion_view.xml',
        'views/promotion_view.xml',
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
