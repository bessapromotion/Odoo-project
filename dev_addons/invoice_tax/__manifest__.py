# -*- coding: utf-8 -*-

{
    'name': 'Invoice Change Tax',
    'version': '15.0',
    'author': 'Deltalog team',
    'category': 'CRM',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Changement de la TVA',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['account', ],
    'data': [

        'wizard/change_tax.xml',
        'views/invoice_view.xml',

    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
