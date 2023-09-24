# -*- coding: utf-8 -*-

from odoo import models, fields, api


# liste des colonnes
def _get_liste(self):
    lst = []
    for a in range(65, 65 + 26):
        lst.append((chr(a), chr(a)))
    return lst


class LeadsImportModel(models.Model):
    _name        = 'leads.import.model'
    _description = 'Model importation des leads'
    _order       = 'name'

    name             = fields.Char   ('Nom du modele', required=True)
    use_number_1     = fields.Selection([('nombre', 'les numeros de colonnes'),
                                         ('lettre', 'les noms des colonnes (lettres)')], string='Utiliser', default='lettre')
    # piece
    col_id           = fields.Integer('Contact ID', default=-1, required=True)
    col_nom          = fields.Integer('Nom', default=-1, required=True)
    col_prenom       = fields.Integer(u'Prénom', default=-1, required=True)
    col_date         = fields.Integer('Date de naissance', default=-1)
    col_adresse      = fields.Integer('Adresse', default=-1, required=True)
    col_phone        = fields.Integer('Phone', default=-1, required=True)
    col_email        = fields.Integer('eMail', default=-1, required=True)
    col_stage        = fields.Integer('Stage', default=-1, required=True)
    col_owner        = fields.Integer('Contact Owner', default=-1, required=True)

    col_a_id       = fields.Selection(_get_liste, string='Contact ID', required=True)
    col_a_nom    = fields.Selection(_get_liste, string='Nom', required=True)
    col_a_prenom        = fields.Selection(_get_liste, string=u'Prénom')
    col_a_date       = fields.Selection(_get_liste, string='Date de naissance')
    col_a_adresse    = fields.Selection(_get_liste, string='Adresse', required=True)
    col_a_phone    = fields.Selection(_get_liste, string='Phone', required=True)
    col_a_email    = fields.Selection(_get_liste, string='eMail', required=True)
    col_a_stage      = fields.Selection(_get_liste, string='Stage', required=True)
    col_a_owner     = fields.Selection(_get_liste, string='Contact Owner', required=True)

    @api.onchange('col_a_id')
    def onchange_a_id(self):
        if self.col_a_id:
            self.col_id = ord(self.col_a_id) - 65
        else:
            self.col_id = -1

    @api.onchange('col_a_nom')
    def onchange_a_nom(self):
        if self.col_a_nom:
            self.col_nom = ord(self.col_a_nom) - 65
        else:
            self.col_nom = -1

    @api.onchange('col_a_prenom')
    def onchange_a_prenom(self):
        if self.col_a_prenom:
            self.col_prenom = ord(self.col_a_prenom) - 65
        else:
            self.col_prenom = -1

    @api.onchange('col_a_date')
    def onchange_a_date(self):
        if self.col_a_date:
            self.col_date = ord(self.col_a_date) - 65
        else:
            self.col_date = -1

    @api.onchange('col_a_adresse')
    def onchange_a_adresse (self):
        if self.col_a_adresse :
            self.col_adresse = ord(self.col_a_adresse) - 65
        else:
            self.col_adresse = -1

    @api.onchange('col_a_phone')
    def onchange_a_phone(self):
        if self.col_a_phone:
            self.col_phone = ord(self.col_a_phone) - 65
        else:
            self.col_phone = -1

    @api.onchange('col_a_email')
    def onchange_a_email(self):
        if self.col_a_email:
            self.col_email = ord(self.col_a_email) - 65
        else:
            self.col_email = -1

    @api.onchange('col_a_stage')
    def onchange_a_stage(self):
        if self.col_a_stage:
            self.col_stage = ord(self.col_a_stage) - 65
        else:
            self.col_stage = -1

    @api.onchange('col_a_owner')
    def onchange_a_owner(self):
        if self.col_a_owner:
            self.col_owner = ord(self.col_a_owner) - 65
        else:
            self.col_owner = -1

    @api.onchange('col_id')
    def onchange_id(self):
        self.col_a_id = ''
        if 0 <= self.col_id <= 25:
            self.col_a_id = chr(self.col_id + 65)

    @api.onchange('col_nom')
    def onchange_nom(self):
        self.col_a_nom = ''
        if 0 <= self.col_nom <= 25:
            self.col_a_nom = chr(self.col_nom + 65)

    @api.onchange('col_prenom')
    def onchange_prenom(self):
        self.col_a_prenom = ''
        if 0 <= self.col_prenom <= 25:
            self.col_a_prenom = chr(self.col_prenom + 65)

    @api.onchange('col_date')
    def onchange_date(self):
        self.col_a_date = ''
        if 0 <= self.col_date <= 25:
            self.col_a_date = chr(self.col_date + 65)

    @api.onchange('col_adresse')
    def onchange_adresse(self):
        self.col_a_adresse = ''
        if 0 <= self.col_adresse <= 25:
            self.col_a_adresse = chr(self.col_adresse + 65)

    @api.onchange('col_phone')
    def onchange_phone(self):
        self.col_a_phone = ''
        if 0 <= self.col_phone <= 25:
            self.col_a_phone = chr(self.col_phone + 65)

    @api.onchange('col_email')
    def onchange_email(self):
        self.col_a_email = ''
        if 0 <= self.col_email <= 25:
            self.col_a_email = chr(self.col_email + 65)

    @api.onchange('col_stage')
    def onchange_stage(self):
        self.col_a_stage = ''
        if 0 <= self.col_stage <= 25:
            self.col_a_stage = chr(self.col_stage + 65)

    @api.onchange('col_owner')
    def onchange_owner(self):
        self.col_a_owner = ''
        if 0 <= self.col_owner <= 25:
            self.col_a_owner = chr(self.col_owner + 65)
