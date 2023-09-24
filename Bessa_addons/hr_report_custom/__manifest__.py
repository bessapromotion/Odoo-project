# -*- coding: utf-8 -*-

{
    'name': 'Rapport RH',
    'version': '15.0',
    'author': 'OMARI Rahma Nour elhouda',
    'license': 'LGPL-3',
    'category': 'HR',
    'sequence': 1,
    'summary': 'Suivre les charges des acquérreurs',
    'description': """ Engagement de confidentialité

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['base', 'mail','hr_base'],
    'data': [
        'report/report_engagement_confidentialite.xml',
        'report/report_menu.xml',
        #'views/autorisation_travaux_view.xml',


    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: