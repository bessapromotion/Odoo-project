# -*- coding: utf-8 -*-

{
    'name': 'Lead import model',
    'version': '15.0',
    'author': 'Deltalog Team',
    'category': 'extra',
    'sequence': 1,
    'website': 'http://www.deltalog-dz.com',
    'summary': 'Modele d\'importation des lead depuis Excel (hubspot)',
    'description': """

    """,
    'images': ['static/description/icon.png',],
    'depends': ['base'],
    'data': ['views/import_model_view.xml',
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
