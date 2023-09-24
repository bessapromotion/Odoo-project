# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': "Base report xlsx",

    'summary': "Base module to create xlsx report",
    'author': 'ACSONE SA/NV,'
              'Creu Blanca,'
              'Odoo Community Association (OCA)',
    'website': "https://github.com/oca/reporting-engine",
    'category': 'Reporting',
    'version': '15.0',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [
            'xlsxwriter',
            'xlrd',
        ],
    },
    'depends': [
        'base', 'web',
    ],
    'data': [
        # 'views/webclient_templates.xml',
    ],
    'demo': [
        'demo/report.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'report_xlsx/static/src/js/report/action_manager_report.js',
    #     ],
    #
    # },
    'installable': True,
}
