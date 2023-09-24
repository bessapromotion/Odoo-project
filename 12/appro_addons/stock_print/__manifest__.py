# -*- coding: utf-8 -*-

{
    'name': 'Stock Print',
    'version': '1.0',
    'author': 'Deltalog Team',
    'category': 'Stock',
    'sequence': 1,
    'website': 'http://www.deltalog-dz.com',
    'description': """

    """,

    'depends': ['stock'],
    'images': ['static/description/icon.png', ],
    'data': [
              # 'views/menu.xml',
              'views/stock_print_view.xml',
              'views/menu_product_view.xml',
              'security/ir.model.access.csv',
              'report/stock_print_report.xml',
              'report/menu.xml',
    ],
    'demo': [],
    'test': [],

    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
