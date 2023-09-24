# -*- coding: utf-8 -*-

{
    'name': 'Fiche Produit - achat',
    'version': '12.0',
    'author': 'Deltalog Team',
    'category': 'Product',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Amélioration Fiche produit pour le module achat',
    'description': """


    """,
    'images': ['static/description/icon.png',],
    'depends': ['product', 'stock' ],
    'data': [
            'security/ir.model.access.csv',
            'views/product_view.xml',
            'views/famille_view.xml',
            # 'data/data.xml',
            'data/res.partner.industry.csv',
             ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
