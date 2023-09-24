# -*- coding: utf-8 -*-

{
    'name': 'Activités Client',
    'version': '15.0',
    'author': 'Deltalog team',
    'license': 'LGPL-3',
    'category': 'CRM',
    'sequence': 1,
    'website': 'http://www.deltalog.dz',
    'summary': 'Enregistrer toutes les activités liées aux clients',
    'description': """
    Enregistrer toutes les activités liées aux clients:
    
    - Visites clients (14012020)
    - Visites employés
    - Appels téléphoniques
    - Boite vocale
    - Rendez-Vous
    
    """,
    'images': ['static/description/icon.png', ],
    'depends': ['crm', 'calendar', 'crm_phonecall', 'hr', 'crm_product'],
    'data': [
        'security/ir.model.access.csv',
        'views/visite_view.xml',
        'views/visite_e_view.xml',
        'views/boite_v_view.xml',
        'views/rdv_view.xml',
        'views/menu_view.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
