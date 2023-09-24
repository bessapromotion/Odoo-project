# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrNiveauScolaire(models.Model):
    _name = 'hr.niveau.scolaire'
    _description = 'Niveau scolaire'

    name = fields.Char('Niveau scolaire', required=True)


class HrEnfant(models.Model):
    _name = 'hr.enfant'
    _description = 'Enfant'

    name = fields.Char(u'Nom et prénom')
    genre = fields.Selection([('male', 'Garcon'), ('female', 'Fille')], string='Genre')

    date_naissance = fields.Date('Date de naissance')
    commune = fields.Char('Commune naissance')
    wilaya_id = fields.Many2one('res.country.state', string='Wilaya')
    pays_id = fields.Many2one(related='wilaya_id.country_id', string='Pays', readonly=True)
    conjoint_id = fields.Many2one('hr.conjoint', string='Conjoint')
    scolarise = fields.Boolean('Scolarisé')
    niveau_scolaire = fields.Many2one('hr.niveau.scolaire', string='Niveau scolaire')
    employe_id = fields.Many2one('hr.employee', string='Employe', check_company=False)
    ayant_droit = fields.Boolean('Ayant droit', default=True)


class HrConjoint(models.Model):
    _name = 'hr.conjoint'
    _description = 'Conjoint'

    name = fields.Char('Nom et prenom')
    date_naissance = fields.Date('Date de naissance')
    presume = fields.Boolean(u'Présumé')
    affililiation = fields.Boolean('Affiliation')
    num_ss = fields.Char(u'Numéro SS')
    nombre_enfant = fields.Integer('Nombre enfants')
    commune = fields.Char('Commune naissance')
    wilaya_id = fields.Many2one('res.country.state', string='Wilaya')
    pays_id = fields.Many2one(related='wilaya_id.country_id', string='Pays', readonly=True)
    mariage_date = fields.Date('Mariage')
    mariage_acte = fields.Date('Acte')
    employe_id = fields.Many2one('hr.employee', string='Employe', check_company=False)
    ayant_droit = fields.Boolean('Ayant droit', default=True)


class Employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    enfant_ids = fields.One2many('hr.enfant', 'employe_id', string='Enfants')
    conjoint_ids = fields.One2many('hr.conjoint', 'employe_id', string='Conjoints')
