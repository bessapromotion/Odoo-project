# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    model_dossier_id = fields.Many2one('hr.dossier.model', string='Modele de dossier')
    date_depot_dossier = fields.Date('Date de depot du dossier')
    piece_ids     = fields.One2many('hr.dossier', 'employe_id', string='Pieces')

    def button_get_piece_liste(self):
        if self.model_dossier_id:
            self.piece_ids.unlink()
            for rec in self.model_dossier_id.piece_ids:
                self.env['hr.dossier'].create({
                    'name' : rec.piece_id.id,
                    'nbr_copie': rec.nbr_copie,
                    # 'date_expiration' : calcul
                    'employe_id' : self.id,
                })
