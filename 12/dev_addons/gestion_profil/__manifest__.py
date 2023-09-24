# -*- coding: utf-8 -*-

{
    'name': 'Gestion des profils',
    'version': '12.0e',
    'author': 'Deltalog team',
    'category': '',
    'sequence': 1,
    'website': 'http://www.deltalog-dz.com',
    'summary': '',
    'description': """

    """,
    'images': ['static/description/icon.png', ],
    'depends': ['base', 'crm_basculement', 'crm_visite', 'crm_phonecall'],
    'data': [
        # groups
        'security/groups_service_commercial.xml',
        'security/groups_service_recouvrement.xml',
        'security/groups_service_admin_vente.xml',
        'security/groups_service_comptabilitee.xml',
        # 'security/groups_direction_general.xml',
        'security/ir.model.access.csv',
        'security/rule.xml',

        # views
        'views/crm_operation.xml',
        'views/crm_catalogue.xml',
        'views/crm_paiement.xml',
        'views/crm_remboursements.xml',
        'views/crm_rapport.xml',
        'views/crm_analyse.xml',
        'views/crm_configuration_root.xml',
        'views/crm.xml',
        'views/projet.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': False,
    'auto_install': False,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
