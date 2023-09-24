# -*- coding: utf-8 -*-

{
    'name': 'Fiche Produit',
    'version': '12.0',
    'author': 'Deltalog Team',
    'category': 'Product',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Amélioration Fiche produit',
    'description': """


    """,
    'images': ['static/description/icon.png',],
    'depends': ['product', 'project', 'sale_crm', 'account', 'sale'],
    'data': [
            'security/ir.model.access.csv',
            # 'security/crm_product_security.xml',

            'views/product_view.xml',
            'views/users_view.xml',
            'views/partner_view.xml',
            'views/order_view.xml',
            'views/invoice_view.xml',
            'views/opportunity_view.xml',
            'data/data.xml',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
