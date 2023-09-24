# -*- coding: utf-8 -*-

{
    'name': 'HR Rapports',
    'version': '15.0',
    'author': 'Deltalog Team',
    'licence': 'LGPL-3',
    'category': 'Human Resources',
    'sequence': 1,
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', ],
    'data': [
            'views/modele_view.xml',
            'security/ir.model.access.csv',
    ],

    'demo': [],
    'test': [],

    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
