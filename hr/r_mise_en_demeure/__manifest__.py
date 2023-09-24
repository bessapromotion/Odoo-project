# -*- coding: utf-8 -*-

{
    'name': 'HR Mise en demeure',
    'version': '14.0e',
    'author': 'Deltalog Team',
    'category': 'hr',
    'sequence': 1,
    'website': '',
    'summary': 'HR Mise en demeure',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['hr_base', 'hr_contract'],
    'data': [
            'views/mise_en_demeure_view.xml',
            'views/parametre_view.xml',
            'data/data.xml',
            'views/sequence.xml',
            'security/ir.model.access.csv',
            'report/reports_menu.xml',
            'report/report_mise_en_demeure_first.xml',
            'report/report_mise_en_demeure_second.xml',
            'report/report_mise_en_demeure_ar.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
