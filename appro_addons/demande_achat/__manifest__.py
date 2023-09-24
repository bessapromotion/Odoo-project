# -*- coding: utf-8 -*-

{
    'name': 'Demande d\'Achat',
    'version': '12.0.0.1',
    'author': 'Deltalog team',
    'category': 'Purchase',
    'sequence': 1,
    'website': '',
    'summary': 'Demande d\'achat',
    'description': """
La gestion des Demandes d'achat internes
========================================

Foctionnalités 
----------------------------------
    * Elaboration de la demande d'achat interne
    * Validation de la demande par le DAL
    * Verification de la disponibilit 
    * Création de la demande d'approvisionnmnt pour les articles en rupture
    * Création des affectations pour les produits disponibles
    * Création d'une consultaiton achat fournisseur
    
    """,
    'images': [
               'static/src/img/icon.png',
               'static/src/img/entete.png',
               'static/src/img/footer.png',
               ],
    'depends': ['purchase', 'purchase_requisition', 'stock', 'hr'],
    'data': [
        # security
        'security/ir.model.access.csv',
        'security/groups.xml',

        'views/picking_view.xml',
        'views/demande_view.xml',
        'views/requisition_view.xml',
        'views/purchase_order_view.xml',
        'views/project_view.xml',
        'data/sequence.xml',
        # 'data/multicompany.xml',
        'wizard/create_document.xml',

        # Reports
        'reports/report_demande_achat.xml',
        # 'reports/report_demande_appro.xml',

        'reports/report_affectation.xml',
        'reports/report_bon_de_commande.xml',
        'reports/report_pv_de_reception.xml',
        'reports/report_fiche_inventaire.xml',
        'reports/report_bon_sortie_magasin.xml',
        'reports/menu_report.xml',

        # Data
        'data/data.xml',
    ],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
