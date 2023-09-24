# -*- coding: utf-8 -*-

{
    'name': 'Gestion de stage',
    'version': '15.0e',
    'author': 'Deltalog team',
    'category': '',
    'sequence': 1,
    'website': 'http://www.deltalog-dz.com',
    'summary': '',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['base', 'hr_base'],
    'data': [
        'security/ir.model.access.csv',
        'report/report_att_stage.xml',
        'report/report_menu.xml',
        'views/hr_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
