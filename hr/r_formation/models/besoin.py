# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class FormationBesoin(models.Model):
    _name = 'formation.besoin'
    _inherit = ['mail.thread']
    _description = 'Besoin en formation'

    @api.depends('res_ids')
    def _nbr_ressources(self):
        for rec in self:
            rec.res_nbr = len(rec.res_ids)

    name = fields.Char(u'Numéro ', default='/', readonly=1)
    date = fields.Date('Date', default=date.today())
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1)
    employe_id = fields.Many2one('hr.employee', string='Responsable de la structure', check_company=False)
    matricule = fields.Char(related='employe_id.matricule', string='Matricule', readonly=1)
    job_id = fields.Many2one('hr.job', string='Fonction')
    department_id = fields.Many2one('hr.department', string=u'Département')
    plan_id = fields.Many2one('formation.plan', string='Plan de formation', required=1, domain="[('state', '=', 'draft'),('actif', '=', True)]", )
    res_nbr = fields.Integer(compute=_nbr_ressources, string='Nombre de ressources', readonly=1)
    res_ids = fields.One2many('formation.besoin.res', 'besoin_id', string='Ressources')
    objectif = fields.Text('Objectif')
    declencheur = fields.Text('Déclencheur')
    impact_business = fields.Text('impact business')
    pre_requis = fields.Text('Pré requis')
    state = fields.Selection([('draft', 'Brouillon'), ('qualifie', 'Qualifié'), ('done', 'Confirmé')], default='draft')

    def action_qualifier(self):
        self.state = 'qualifie'

    def confirm_alimenter_plan(self):
        self.state = 'done'
        for rec in self.res_ids:
            if not rec.theme_id and rec.state != 'cancel':
                raise UserError(_(u'Veuillez indiquer le thème de la formation pour %s', rec.name.name))
        for rec in self.res_ids:
            if rec.state != 'cancel':
                rec.state = 'done'
                line = self.env['formation.plan.line'].search([('plan_id', '=', self.plan_id.id), ('theme_id', '=', rec.theme_id.id)])
                if line.exists():
                    res = self.env['formation.plan.line.res'].search([('plan_line_id', '=', line.id), ('name', '=', rec.name.id)])
                    if not res.exists():
                        self.env['formation.plan.line.res'].create({
                            'name': rec.name.id,
                            'plan_line_id': line.id,
                        })
                else:
                    ln = self.env['formation.plan.line'].create({
                        'theme_id': rec.theme_id.id,
                        'plan_id': self.plan_id.id,
                    })
                    self.env['formation.plan.line.res'].create({
                        'name': rec.name.id,
                        'plan_line_id': ln.id,
                    })

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('formation.besoin') or '/'
        vals['job_id'] = self.env['hr.employee'].browse(vals.get('employe_id')).job_id.id
        vals['department_id'] = self.env['hr.employee'].browse(vals.get('employe_id')).department_id.id

        return super(models.Model, self).create(vals)

    def unlink(self):
        self.res_ids.unlink()
        return super(models.Model, self).unlink()

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id:
                rc.job_id = rc.employe_id.job_id.id
                rc.department_id = rc.employe_id.department_id.id
            else:
                rc.job_id = None
                rc.department_id = None


class FormationBesoinRessource(models.Model):
    _name = 'formation.besoin.res'
    _description = 'Ressources de la formation'

    name = fields.Many2one('hr.employee', string='Ressource', required=1, check_company=False)
    job_id = fields.Many2one(related='name.job_id', string='Fonction', readonly=1)
    department_id = fields.Many2one(related='name.department_id', string=u'Département', readonly=1)
    csp_id = fields.Many2one(related='name.csp_id', string=u'CSP', readonly=1)
    besoin_action = fields.Char(u"Désignation de l’action de formation", required=True)
    besoin_id = fields.Many2one('formation.besoin', string='Besoin en Formation')
    theme_id = fields.Many2one('formation.theme', string='Theme de la Formation')
    state = fields.Selection([('draft', 'brouillon'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    motif = fields.Text('Motif d\'annulation')

    def action_cancel(self):
        self.state = 'cancel'
        return {
            'name': _('Annulation'),
            'view_mode': 'form',
            'res_model': 'formation.besoin.res.motif.wizard',
            'view_id': self.env.ref('r_formation.formation_besoin_res_motif_wizard_form_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_res_id': self.id,
            },
            'target': 'new',
        }
