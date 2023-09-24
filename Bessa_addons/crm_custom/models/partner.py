# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    @api.depends('visite_ids')
    def _nbr_visites(self):
        nbr = 0
        for rec in self:
            for line in rec.visite_ids:
                if line.state == 'valid':
                    nbr += 1
            rec.nbr_visites = nbr
        self.flush()
        self.update_state_potentiel()

    @api.onchange('nbr_visites')
    def update_state_potentiel(self):
        for rec in self:
            if rec.etat == 'Prospect' and rec.nbr_visites > 1:
                rec.etat = 'Potentiel'

    etat = fields.Selection([('Prospect', 'Prospect'),
			     ('signataire', 'Signataire'),
                             ('proprietaire', 'Propriétaire'),
                             ('Potentiel', 'Potentiel'),
                             ('Réservataire', 'Réservataire'),
                             ('Acquéreur', 'Acquéreur'),
                             ('Locataire', 'Locataire'),
                             ('Client Perdu', 'Client Perdu'),
                             ], string='Etat', default='Prospect', required=1, tracking=True)
    visite_ids = fields.One2many('crm.visite', 'name', string='Visite')
    nbr_visites = fields.Integer(compute=_nbr_visites, string='Nombre de Visites', store=True)
    mobile = fields.Char(required=1, tracking=1)
    email = fields.Char(required=1, tracking=1)
    name = fields.Char(index=True, tracking=1)
