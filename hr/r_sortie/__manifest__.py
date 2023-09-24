# -*- coding: utf-8 -*-

{
    'name': 'Mouvements RH',
    'version': '14.0e',
    'author': 'Deltalog team',
    'licence': 'LGPL-3',
    'category': '',
    'sequence': 1,
    'website': 'http://www.deltalog-dz.com',
    'summary': '',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_employee_sortie.xml',
        'views/hr_employee_recup.xml',
        'views/hr_employee_absence.xml',
        'views/sequence.xml',
        'report/report_bon_sortie.xml',
        'report/report_bon_recup.xml',
        'report/report_auto_absence.xml',
        'report/report_menu.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
