# -*- coding: utf-8 -*-

{
    'name': 'additional information',
    'version': '12.0',
    'author': 'Deltalog Team',
    'category': 'Partner',
    'sequence': 1,
    'website': 'http://www.deltalog.com',
    'summary': 'additional company & Partner information ',
    'description': """

    """,
    'images': ['static/description/icon.png',],
    'depends': ['purchase'],
    'data': [
            'views/partner_view.xml',
            'views/res_bank_view.xml',
            'views/company_view.xml',
            'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
