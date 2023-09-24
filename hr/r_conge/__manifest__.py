# -*- coding: utf-8 -*-

{
    'name': 'HR Droit congé annuel',
    'version': '14.0e',
    'author': 'Deltalog team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Calcul des droits de congé annuels',
    'description': """
- Calcul les droits aux congés du personnel
- Créés automatiquement les attributions congés dans le module Time Off
    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_holidays', 'hr_base'],
    'data': [
        'data/data.xml',
        'views/conge_view.xml',
        'views/hr_leave.xml',
        # 'views/cr_view.xml',
        'views/ferie_view.xml',
        'views/allocation_view.xml',
        # 'views/param_view.xml',
        # 'views/sequence.xml',
        'security/ir.model.access.csv',
        'report/reports_menu.xml',
        'report/report_demande_conge_exceptionnel.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
