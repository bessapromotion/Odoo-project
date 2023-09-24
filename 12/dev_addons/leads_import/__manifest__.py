# -*- coding: utf-8 -*-

{
    'name': 'Leads import',
    'version': '1.0',
    'author': 'Deltalog Team',
    'category': 'extra',
    'sequence': 1,
    'website': 'http://www.deltalog-dz.com',
    'summary': 'Importation des leads depuis Excel (hubspots)',
    'description': """

    """,
    'images': ['static/description/icon.png',],
    'depends': ['crm_product', 'lead_import_model'],
    'data': [
        'wizard/import_leads_view.xml',
        'data/data.xml',
        # 'views/partner_view.xml',
        # 'views/users_view.xml',
        'views/lifecycle_view.xml',
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
