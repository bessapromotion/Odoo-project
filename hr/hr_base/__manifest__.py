# -*- coding: utf-8 -*-


{
    'name': 'HR Fiche Employé',
    'version': '14.0e',
    'author': 'Deltalog Team',
    'category': 'hr',
    'sequence': 1,
    'website': 'www.deltalog.dz',
    'summary': 'Complément d\'informations employé',
    'description': """
    version 1.0 du 08 07 2020

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr', 'hr_recruitment'],
    'data': [
        'data/data.xml',
        'wizard/motif_at.xml',
        'views/hr_view.xml',
        'views/hr_hide_menu.xml',
        'views/job_view.xml',
        'views/company_view.xml',
        'views/hr_applicant.xml',
        'views/placement_type.xml',
        'views/menu_view.xml',
        'views/historique_view.xml',
        'views/sequence.xml',
        'security/groups.xml',
        'security/rule.xml',
        'security/ir.model.access.csv',
        'reports/layouts.xml',
        'reports/report_attestation_travail.xml',
        'reports/report_certificat_travail.xml',
        'reports/report_fgp.xml',
        # 'reports/report_fiche_renseignement.xml',
        'reports/report_fiche_signaletique.xml',
        'reports/report_menu.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
