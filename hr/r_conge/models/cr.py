# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError


class CongeRecuperation(models.Model):
    _name = 'hr.conge.recuperation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Calcul du congé de récupération'

    @api.depends('lattrib_ids')
    def _attrib_nbr(self):
        for rec in self:
            rec.lattrib_nbr = len(rec.lattrib_ids)

    name        = fields.Char(u'Numéro', default='/', readonly=1, required=True)
    date_start  = fields.Date(u'Date début', required=True, readonly=1, states={'draft': [('readonly', False)]})
    date_end    = fields.Date(u'Date fin', required=True, readonly=1, states={'draft': [('readonly', False)]})
    user_id     = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1, states={'draft': [('readonly', False)]})
    site_id     = fields.Many2one('res.partner', string='Site', domain="[('site', '=', True)]", readonly=1, states={'draft': [('readonly', False)]})
    region_id = fields.Many2one(related='site_id.region_id', string=u'Région')
    observation = fields.Text('Observation')
    date        = fields.Date('Date etablissement', default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    line_ids    = fields.One2many('hr.conge.recuperation.line', 'conge_id', string='Détail', readonly=1)
    # lattrib_ids = fields.One2many('hr.leave.allocation', 'source_id', string='Allocation de congé', readonly=1)
    # lattrib_nbr = fields.Integer(compute=_attrib_nbr, string='Nombre d\'attributions')
    state       = fields.Selection([('draft', 'Nouveau'),
                                    ('load', 'En cours'),
                                    ('compute', 'Calculé'),
                                    ('done', 'Terminé'),
                                    ('cancel', 'Annulé')], string='Etat', default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = vals['date_start'][:4] + '/' + vals['date_end'][:4]

        return super(models.Model, self).create(vals)

    @api.onchange('date_start')
    def onchange_date_start(self):
        if self.date_start:
            self.date_end = str(int(str(self.date_start)[:4])+1) + '-06-30'

    def action_load(self):
        self.state = 'load'
        self.line_ids.unlink()
        liste = self.env['hr.employee'].search([('active', '=', True),
                                                ('site_id', '=', self.site_id.id),
                                                ('contract_id', '!=', None),
                                                ])
        for rec in liste:
            self.env['hr.conge.recuperation.line'].create({
                'employe_id'  : rec.id,
                'conge_id'    : self.id,
                'matricule'   : rec.matricule,
                'job_id'      : rec.job_id.id,
                'regime_id'   : rec.contract_id.type_id.id,
                'date_entree' : rec.contract_id.date_entree,
            })
        # self.line_ids = line

    def action_compute(self):

        self.state = 'compute'
        # nombre de mois travaillé
        # au sud ou au nord
        # par rapport au contrat et aux avenants
        # si mois commence aprés le 15 il n'est pas pris en charge

        for rec in self.line_ids:
            if rec.date_entree > self.date_start:
                if int(rec.date_entree.strftime("%d")) > 15:
                    rec.date_debut = rec.date_entree.strftime("%Y") + '-' + "{0:0>2}".format(str((int(rec.date_entree.strftime("%m"))+1))) + '-01'
                else:
                    rec.date_debut = rec.date_entree.strftime("%Y") + '-' + rec.date_entree.strftime("%m") + '-01'
            else:
                rec.date_debut = self.date_start

            if int(rec.date_debut.strftime("%m")) > 6:
                rec.nbr_mois = 12 - int(rec.date_debut.strftime("%m")) + 7
            else:
                rec.nbr_mois = 12 - int(rec.date_debut.strftime("%m")) - 5

            rec.nbr_jour = rec.nbr_mois * rec.region_id.nbr_jour

    def action_create_attribution(self):
        for rec in self.line_ids:
            self.env['hr.leave.allocation'].create({
                'name'             : 'Congé annuel ' + str(self.date_start)[:4] + '/' + str(self.date_end)[:4],
                'employee_id'      : rec.employe_id.id,
                'holiday_status_id': 1,
                'allocation_type'  : 'regular',
                'number_of_days'   : rec.nbr_jour,
                'holiday_type'     : 'employee',
                'state'            : 'validate',
                'source_id'        : self.id,
            })

    def action_validate(self):
        # self.state = 'done'
        self.action_create_attribution()

    def action_cancel(self):
        self.state = 'cancel'

    def unlink(self):
        if self.state not in ('draft', 'load'):
            raise UserError(_('Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
        return super(models.Model, self).unlink()


class CongeRecuperationLine(models.Model):
    _name = 'hr.conge.recuperation.line'
    _description = u'Détail du pointage'

    name        = fields.Char('code', readonly=1, default='/')
    conge_id    = fields.Many2one('hr.conge.recuperation', string='conge de recuperation')
    employe_id  = fields.Many2one('hr.employee', string='Employé', check_company=False)
    matricule   = fields.Char('Matricule')
    date_entree = fields.Date('Date entrée')
    regime_id   = fields.Many2one('hr.contract.type', string='Régime de travail')
    job_id      = fields.Many2one('hr.job', string='Poste')
    date_debut  = fields.Date('Date debut comptage')
    nbr_mois    = fields.Integer('nombre mois')
    nbr_jour    = fields.Float('Nombre jours')

    @api.onchange('employe_id')
    def onchange_employe(self):
        if self.employe_id:
            self.matricule = self.employe_id.matricule
            self.regime_id = self.employe_id.contract_id.regime_id.id
            self.date_entree = self.employe_id.contract_id.date_start
            self.job_id = self.employe_id.contract_id.job_id.id
        else:
            self.matricule = ''
            self.regime_id = None
            self.date_entree = ''
            self.job_id    = None

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            mat = ''
            if vals['matricule']:
                mat = vals['matricule']
            vals['name'] = self.env['hr.conge.recuperation'].browse(vals['conge_id']).name + '/' + mat

        return super(models.Model, self).create(vals)
