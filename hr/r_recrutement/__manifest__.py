# -*- coding: utf-8 -*-

{
    'name': 'Processus de recrutement',
    'version': '14.0e',
    'author': 'Deltalog team',
    'category': '',
    'sequence': 1,
    'website': 'http://www.deltalog-dz.com',
    'summary': '',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'hr_recruitment', 'r_piece_dossier'],
    'data': [
        'views/applicant_view.xml',
        'report/report_promesse_embauche.xml',
        'report/report_poste.xml',
        'report/report_menu.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
