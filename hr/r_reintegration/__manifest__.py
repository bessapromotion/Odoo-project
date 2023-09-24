# -*- coding: utf-8 -*-

{
    'name': 'HR Réintegration',
    'version': '13.0e',
    'author': 'Deltalog team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Réintegration',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'r_contract', 'r_avenant', 'r_frt'],
    'data': [
            'views/reintegration_view.xml',
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
