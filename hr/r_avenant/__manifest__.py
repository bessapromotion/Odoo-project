# -*- coding: utf-8 -*-

{
    'name': 'Avenant au contrat',
    'version': '13.0',
    'author': 'Deltalog Team',
    'category': 'Human Resources',
    'sequence': 1,
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['r_contract', 'hr_dynamic_reports'],
    'data': [
        'views/avenant_view.xml',
        'wizard/create_avenant_view.xml',
        'wizard/create_rnv_view.xml',
        'report/report_avenant_contrat.xml',
        'report/report_menu.xml',
        'security/ir.model.access.csv',

    ],

    'demo': [],
    'test': [],

    'installable': True,
    'application': False,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
