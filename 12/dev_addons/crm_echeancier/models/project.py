# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    @api.depends('bien_ids')
    def _comptage_bien(self):
        for rec in self:
            b = 0
            r = 0
            p = 0
            v = 0
            rec.nbr_biens = len(rec.bien_ids)
            for line in rec.bien_ids:
                if line.etat == 'Libre':
                    b += 1
                if line.etat == 'Réservé':
                    r += 1
                if line.etat == 'Pré-Réservé':
                    p += 1
                if line.etat == 'Livré':
                    v += 1

            rec.nbr_libre = b
            rec.nbr_reserv = r
            rec.nbr_preres = p
            rec.nbr_livre = v

    ech_modele_id   = fields.Many2one('echeancier.modele', string='Modele echeancier')
    echeancier_modele_ids  = fields.One2many('project.echeancier.modele.line', 'project_id', string='Echeancier modele')
    echeancier_ids  = fields.One2many('project.echeancier.line', 'project_id', string='Echeancier')
    date_debut = fields.Date('Date début')
    duree_estimee = fields.Integer('Durée estimée (mois)')
    date_fin   = fields.Date('Date prévue de livraison')

    taux_avancement = fields.Integer('Taux d\'avancement')
    taux_avancement_pi = fields.Integer(related='taux_avancement', string='Taux d\'avancement')

    # adresse du projet
    code         = fields.Char('Code', required=True)
    # default_code = fields.Char('Code')
    street     = fields.Char('Rue')
    street2    = fields.Char('Rue 2')
    city       = fields.Char('Cité')
    commune_id = fields.Many2one('res.commune', string='Commune')
    state_id   = fields.Many2one('res.country.state', string='Wilaya')
    zip = fields.Char('ZIP')
    country_id = fields.Many2one('res.country', string='Pays', default=113)

    bien_ids   = fields.One2many('product.product', 'project_id', string='Biens')
    nbr_biens  = fields.Integer(compute=_comptage_bien, string='Nombre de biens')
    nbr_libre  = fields.Integer(compute=_comptage_bien, string='Biens libres')
    nbr_reserv = fields.Integer(compute=_comptage_bien, string='Biens réservés')
    nbr_preres = fields.Integer(compute=_comptage_bien, string='Biens pré-réservés')
    nbr_livre  = fields.Integer(compute=_comptage_bien, string='Biens Livrés')

    @api.one
    def appliquer_echeancier_modele(self):
        if self.ech_modele_id:
            self.echeancier_modele_ids.unlink()
            for rec in self.ech_modele_id.echeance_ids:
                self.env['project.echeancier.modele.line'].create({
                    'name'      : rec.name,
                    'taux_av'   : rec.taux_av,
                    'taux_py'   : rec.taux_py,
                    'nbr_jour'  : rec.nbr_jour,
                    'project_id': self.id,
                })

    @api.one
    def maj_echeancier(self):
        if self.echeancier_modele_ids:
            self.echeancier_ids.unlink()
            taux = 0
            add  = False
            for rec in self.echeancier_modele_ids:
                if rec.taux_av < self.taux_avancement:
                    taux += rec.taux_py
                else:
                    if not add:
                        add = True
                        taux += rec.taux_py
                        self.env['project.echeancier.line'].create({
                            'name': rec.name,
                            'taux_av': rec.taux_av,
                            'taux_py': taux,
                            # 'date': rec.nbr_jour,
                            'project_id': self.id,
                        })
                    else:
                        self.env['project.echeancier.line'].create({
                            'name': rec.name,
                            'taux_av': rec.taux_av,
                            'taux_py': rec.taux_py,
                            # 'date': rec.nbr_jour,
                            'project_id': self.id,
                        })


class ProjectEcheancierModele(models.Model):
    _name = 'project.echeancier.modele.line'
    _description = 'Echeance'
    # _order = 'date'

    name       = fields.Char('Echeance')
    taux_av    = fields.Integer('Taux d\'avancement')
    taux_py    = fields.Integer('Taux de paiement')
    nbr_jour   = fields.Integer('Nombre de jours')
    project_id = fields.Many2one('project.project', string='Projet')


class ProjectEcheancier(models.Model):
    _name = 'project.echeancier.line'
    _description = 'Echeance'
    # _order = 'date'

    name       = fields.Char('Echeance')
    taux_av    = fields.Integer('Taux d\'avancement')
    taux_py    = fields.Integer('Taux de paiement', required=1)
    date       = fields.Date('Date echeance', required=1)
    project_id = fields.Many2one('project.project', string='Projet', required=1)
