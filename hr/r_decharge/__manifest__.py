# -*- coding: utf-8 -*-

{
    'name': 'Gestion des décharge',
    'version': '14.0e',
    'author': 'Deltalog team',
    'category': '',
    'sequence': 1,
    'website': 'http://www.deltalog-dz.com',
    'summary': '',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', ],
    'data': [
        'views/decharge.xml',
        'views/sequence.xml',
        'report/report_decharge.xml',
        'report/reports_menu.xml',
        'security/rule.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
