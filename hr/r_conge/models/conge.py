# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError


class Conge(models.Model):
    _name = 'hr.conge'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Calcul du congé'
    _order = 'name desc'

    @api.depends('lattrib_ids')
    def _attrib_nbr(self):
        for rec in self:
            rec.lattrib_nbr = len(rec.lattrib_ids)

    name = fields.Char(u'Annee', default='/', required=True, readonly=1)
    date_start = fields.Date(u'Date début', required=True, readonly=1, states={'draft': [('readonly', False)]})
    date_end = fields.Date(u'Date fin', required=True, readonly=1, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    observation = fields.Text('Observation')
    date = fields.Date('Date établissement', default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('hr.conge.line', 'conge_id', string='Détail', readonly=1)
    lattrib_ids = fields.One2many('hr.leave.allocation', 'source_id', string='Allocation de congé', readonly=1)
    lattrib_nbr = fields.Integer(compute=_attrib_nbr, string='Nombre d\'attributions')
    state = fields.Selection([('draft', 'Nouveau'),
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
            self.date_end = str(int(str(self.date_start)[:4]) + 1) + '-06-30'

    def action_load(self):
        # corriger contrat
        ctr = self.env['hr.contract'].search([('state', '=', 'open')])
        for rec in ctr:
            rec.employee_id.contract_id = rec.id

        self.state = 'load'
        self.line_ids.unlink()
        liste = self.env['hr.employee'].search([('active', '=', True), ('contract_id', '!=', None)])
        for rec in liste:
            # print (rec.name)
            if not rec.contract_id.date_entree and rec.contract_id.state not in ('draft', 'cancel'):
                raise UserError(_(u'Date entrée non renseignée dans le contrat de l\'employé [' + rec.name + ']'))
            if rec.contract_id.state not in ('draft', 'cancel'):
                if rec.contract_id.date_entree < self.date_end:
                    self.env['hr.conge.line'].create({
                        'employe_id': rec.id,
                        'conge_id': self.id,
                        'matricule': rec.barcode,
                        'job_id': rec.job_id.id,
                        'contract_id': rec.contract_id.id,
                        'department_id': rec.department_id.id,
                        'date_entree': rec.contract_id.date_entree,
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
                dd = int(rec.date_entree.strftime("%d"))
                if int(rec.date_entree.strftime("%d")) > 15:
                    if rec.date_entree.strftime("%m") < '12':
                        rec.date_debut = rec.date_entree.strftime("%Y") + '-' + "{0:0>2}".format(
                            str((int(rec.date_entree.strftime("%m")) + 1))) + '-01'
                    else:
                        rec.date_debut = str(int(rec.date_entree.strftime("%Y")) + 1) + "-01-01"
                else:
                    rec.date_debut = rec.date_entree.strftime("%Y") + '-' + rec.date_entree.strftime("%m") + '-01'
            else:
                rec.date_debut = self.date_start.strftime("%Y") + '-07-01'

            if rec.date_debut < self.date_end:
                if int(rec.date_debut.strftime("%m")) > 6:
                    rec.nbr_mois = 12 - int(rec.date_debut.strftime("%m")) + 7
                else:
                    rec.nbr_mois = 12 - int(rec.date_debut.strftime("%m")) - 5
            else:
                rec.nbr_mois = 0

            rec.nbr_jour = rec.nbr_mois * 2.5  # rec.region_id.nbr_jour

    def action_create_attribution(self):
        for rec in self.line_ids:
            if rec.nbr_jour > 0:
                self.env['hr.leave.allocation'].create({
                    'name': 'Congé annuel ' + str(self.date_start)[:4] + '/' + str(self.date_end)[:4],
                    'employee_id': rec.employe_id.id,
                    'holiday_status_id': 1,
                    'allocation_type': 'regular',
                    'number_of_days': rec.nbr_jour,
                    'holiday_type': 'employee',
                    'state': 'validate',
                    'source_id': self.id,
                })

    def action_validate(self):
        self.state = 'done'
        self.action_create_attribution()

    def action_cancel(self):
        self.state = 'cancel'

    def unlink(self):
        if self.state == 'done':
            raise UserError(_(
                'Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
        self.line_ids.unlink()
        return super(models.Model, self).unlink()


class CongeLine(models.Model):
    _name = 'hr.conge.line'
    _description = u'Détail du pointage'

    name = fields.Char('code', readonly=1, default='/')
    conge_id = fields.Many2one('hr.conge', string='Congé annuel')
    employe_id = fields.Many2one('hr.employee', string='Employé', check_company=False)
    matricule = fields.Char(string='Matricule')
    date_entree = fields.Date('Date entrée')
    contract_id = fields.Many2one('hr.contract', string='Contract')
    contract_state = fields.Selection(related='contract_id.state', string='Etat')
    department_id = fields.Many2one('hr.department', string=u'Département')
    job_id = fields.Many2one('hr.job', string='Poste')
    date_debut = fields.Date('Date debut comptage')
    nbr_mois = fields.Integer('nombre mois')
    nbr_jour = fields.Float('Nombre jours')

    @api.onchange('employe_id')
    def onchange_employe(self):
        if self.employe_id:
            self.matricule = self.employe_id.barcode
            self.contract_id = self.employe_id.contract_id.id
            self.department_id = self.employe_id.department_id.id
            self.date_entree = self.employe_id.contract_id.date_start
            self.job_id = self.employe_id.contract_id.job_id.id
        else:
            self.matricule = ''
            self.department_id = None
            self.contract_id = None
            self.date_entree = ''
            self.job_id = None

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            mat = ''
            if vals['matricule']:
                mat = vals['matricule']
            vals['name'] = self.env['hr.conge'].browse(vals['conge_id']).name + '/' + mat

        return super(models.Model, self).create(vals)
