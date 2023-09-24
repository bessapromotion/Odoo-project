# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class Demande(models.Model):
    _name = 'formation.demande'
    _inherit = ['mail.thread']
    _description = 'Demande de formation'

    @api.depends('res_ids')
    def _nbr_ressources(self):
        for rec in self:
            rec.res_nbr = len(rec.res_ids)

    name = fields.Char(u'Numéro ', default='/', readonly=1)
    date = fields.Date('Date', default=date.today())
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1)
    employe_id = fields.Many2one('hr.employee', string='Demandeur', check_company=False)
    matricule = fields.Char(related='employe_id.matricule', string='Matricule', readonly=1)
    job_id = fields.Many2one(related='employe_id.job_id', string='Fonction')
    department_id = fields.Many2one(related='employe_id.department_id', string='Departement')
    plan_id = fields.Many2one('formation.plan', string='Plan de formation', domain="[('state', '=', 'draft'),('actif', '=', True)]")
    typologie_id = fields.Many2one('formation.typologie', string='Typologie', states={'done': [('required', True)]})
    theme_id = fields.Many2one('formation.theme', string='Formation', states={'done': [('required', True)]})
    categorie_id = fields.Many2one(related='theme_id.categorie_id', string='Categorie')
    besoin_action = fields.Char(u"Intitulé de formation", required=True)
    motif = fields.Text('Motif')
    commentaire = fields.Text('Commentaire')
    res_nbr = fields.Integer(compute=_nbr_ressources, string='Nombre de ressources', readonly=1)
    res_ids = fields.One2many('formation.demande.res', 'besoin_id', string='Ressources')
    objectif = fields.Text('Objectif')
    state = fields.Selection([('draft', 'Nouveau'),
                              ('done', u'Validé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('formation.demande') or '/'
        # vals['job_id'] = self.env['hr.employee'].browse(vals.get('employe_id')).job_id.id
        # vals['department_id'] = self.env['hr.employee'].browse(vals.get('employe_id')).department_id.id

        if vals['plan_id']:
            self.env['formation.plan.line'].create({
                'name': self.env['ir.sequence'].get('formation.plan.line') or '/',
                'plan_id': vals.get('plan_id'),
                'theme_id': vals.get('theme_id'),
            })

        return super(models.Model, self).create(vals)

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id:
                rc.job_id = rc.employe_id.job_id.id
                rc.department_id = rc.employe_id.department_id.id
            else:
                rc.job_id = None
                rc.department_id = None

    def action_validate(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def action_print(self):
        return self.env.ref('r_formation.act_report_besoin_formation').report_action(self)


class FormationDemandeRessource(models.Model):
    _name = 'formation.demande.res'
    _description = 'Ressources de la formation'

    name = fields.Many2one('hr.employee', string='Ressource', required=1, check_company=False)
    job_id = fields.Many2one(related='name.job_id', string='Fonction', readonly=1)
    department_id = fields.Many2one(related='name.department_id', string=u'Département', readonly=1)
    csp_id = fields.Many2one(related='name.csp_id', string=u'CSP', readonly=1)
    besoin_id = fields.Many2one('formation.demande', string='Besoin en Formation', ondelete='cascade')
