# -*- coding: utf-8 -*-


{
    'name': 'HR Fiche Employé verrouillée',
    'version': '14.0e',
    'author': 'Deltalog Team',
    'category': 'hr',
    'sequence': 1,
    'website': 'www.deltalog.dz',
    'summary': 'Fiche verrouillée si employé inactif',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'r_piece_dossier', 'r_service_national'],
    'data': [
        'views/hr_view.xml',
        'views/hr_piece_dossier.xml',
        'views/service_national.xml',
            ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
