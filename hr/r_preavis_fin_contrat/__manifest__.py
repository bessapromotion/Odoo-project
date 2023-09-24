# -*- coding: utf-8 -*-

{
    'name': 'HR Préavis Fin de Contrat',
    'version': '13.0e',
    'author': 'Deltalog Team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Préavis Fin de Contrat',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'hr_contract'],
    'data': [
            'views/preavis_view.xml',
            'views/sequence.xml',
            'security/ir.model.access.csv',
            'report/reports_menu.xml',
            'report/report_preavis_fin_contrat.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
