# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class Piece(models.Model):
    _name = 'hr.dossier.piece'
    _description = 'Piece a fournir'

    name = fields.Char('Piece')
    validite = fields.Integer('Durée validité (Jour)')


class DossierModel(models.Model):
    _name = 'hr.dossier.model'
    _description = 'Modele de dossier'

    name = fields.Char('Nom du modele')
    piece_ids = fields.One2many('hr.dossier.model.piece', 'model_id', string='Pieces')
    file = fields.Binary('Dossier', company_dependent=True)

    def unlink(self):
        self.piece_ids.unlink()
        return super(DossierModel, self).unlink()


class DossierModelPiece(models.Model):
    _name = 'hr.dossier.model.piece'
    _description = 'Piece du modele'

    name = fields.Integer('Numero')
    piece_id = fields.Many2one('hr.dossier.piece', string='Piece')
    nbr_copie = fields.Integer('Nombre de copie', default=1)
    model_id = fields.Many2one('hr.dossier.model', string='Modele de dossier')


class Dossier(models.Model):
    _name = 'hr.dossier'
    _description = 'Dossier a fournir'

    name = fields.Many2one('hr.dossier.piece', string='Piece')
    nbr_copie = fields.Integer('Nombre de copie')
    validite = fields.Integer(related='name.validite', string='Durée validité (Jour)')
    # reste         = fields.Integer(compute='', string='Jours restants')
    date = fields.Date('Date etablissement', default=date.today())
    date_expiration = fields.Date('Date expiration')
    recue = fields.Boolean('Déposé', default=False)
    state = fields.Selection(
        [('NonRemis', 'Non Remis'), ('Remis', 'Remis'), ('NonDemand', 'Non demandé'), ('expir', 'Expirée')],
        string='Etat', default='NonRemis')
    employe_id = fields.Many2one('hr.employee', string='employé', check_company=True)

    # candidat_id = fields.Many2one('hr.applicant', string='candidat')

    def action_recue(self):
        self.state = 'Remis'

    def action_nondemande(self):
        self.state = 'NonDemand'
