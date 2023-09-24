# -*- coding: utf-8 -*-

{
    'name': 'Analyse Ressource Humaines',
    'version': '14.0e',
    'author': 'Deltalog team',
    'category': '',
    'sequence': 1,
    'website': 'http://www.deltalog-dz.com',
    'summary': '',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'r_frt', 'hr_company'],
    'data': [
        'security/ir.model.access.csv',
        'security/rule.xml',
        'views/hr_ems.xml',
        'views/hr_historique.xml',
        'views/trial.xml',
        'views/contract_end.xml',
        'wizard/hr_ems_wizard.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
