# -*- coding: utf-8 -*-

from odoo import models, fields


class EcheancierModele(models.Model):
    _name = 'echeancier.modele'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Modele echeancier'

    name  = fields.Char('Nom du modele echeancier', required=True)
    echeance_ids  = fields.One2many('echeancier.modele.line', 'modele_id', string='Echeancier modele')
    description = fields.Text('Description')
    active = fields.Boolean('Actif', default=True)


class EcheancierModeleLine(models.Model):
    _name = 'echeancier.modele.line'
    _description = 'Echeancier lignes'
    # _order = 'taux_av'

    name = fields.Char('Echeance')
    taux_av = fields.Integer('Taux d avancement')
    taux_py = fields.Integer('Taux de paiement')
    nbr_jour = fields.Integer('Nombre de jours')
    modele_id = fields.Many2one('echeancier.modele', string='Modele')
