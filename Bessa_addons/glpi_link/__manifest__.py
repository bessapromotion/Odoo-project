{
    'name': 'GLPI Link',
    'version': '0.1',
    'summary': "Module pour ajouter un lien vers GLPI dans les commandes d'achat",
    'description': "Ce module ajoute un champ lien vers GLPI dans les commandes d'achat",
    'category': 'Purchases',
    'license': 'AGPL-3',
    'author': 'Messaoudi Abderraouf',
    'depends': ['purchase'],
    'data': [
        'views/purchase_order_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
