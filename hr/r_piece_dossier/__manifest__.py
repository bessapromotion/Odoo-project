# -*- coding: utf-8 -*-

{
    'name': 'HR Dossier d\'embauche',
    'version': '14.0e',
    'author': 'Deltalog Team',
    'category': 'hr',
    'sequence': 1,
    'website': 'www.deltalog.dz',
    'summary': 'Dossier d\'embauche',
    'description': """

    """,
    'images':
        [
            'static/description/icon.png',
        ],
    'depends': ['hr', ],
    'data': [
        'views/piece_view.xml',
        # 'views/applicant_view.xml',
        'views/hr_view.xml',
        'data/data.xml',
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
