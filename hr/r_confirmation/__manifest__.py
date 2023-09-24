# -*- coding: utf-8 -*-

{
    'name': 'HR Confirmation',
    'version': '13.0e',
    'author': 'Deltalog team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Confirmation',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base'],
    'data': [
            'views/confirmation_view.xml',
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
