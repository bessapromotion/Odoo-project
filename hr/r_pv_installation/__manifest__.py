# -*- coding: utf-8 -*-

{
    'name': 'HR PV Installation',
    'version': '14.0e',
    'author': 'Deltalog team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR PV Installation',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'r_contract', 'hr_company'],
    'data': [
            'views/installation_view.xml',
            'views/contract.xml',
            'views/pv_parametre.xml',
            'views/sequence.xml',
            'security/ir.model.access.csv',
            'report/reports_menu.xml',
            'report/report_pv_installation_rh.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
