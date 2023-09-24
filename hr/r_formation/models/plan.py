# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import datetime
from odoo.exceptions import UserError, ValidationError


class FormationPlan(models.Model):
    _name = 'formation.plan'
    _inherit = ['mail.thread']
    _description = 'Plan de formation'

    @api.depends('besoin_ids')
    def _nbr_fiche(self):
        for rec in self:
            rec.nbr_fiche = len(rec.besoin_ids)

    @api.depends('session_ids')
    def _nbr_session(self):
        for rec in self:
            rec.nbr_session = len(rec.session_ids)

    @api.depends('session_ids.cout')
    def _budget_reel(self):
        for rec in self:
            rec.cout_real = sum(line.cout for line in rec.session_ids)

    @api.depends('line_ids.cout_prev', 'line_ids.session_ids.cout')
    def _cout_global(self):
        for rec in self:
            rec.budget = sum(line.cout_prev for line in rec.line_ids)
            rec.budget_real = sum(line.cout_real for line in rec.line_ids)

    name = fields.Char(u'Numéro ', default='/', readonly=1)
    objet = fields.Char('Objet')
    exercice = fields.Char('Exercice', size=4, readonly=1, states={'draft': [('readonly', False)]})
    objectif = fields.Text('Strategie et objectif global')
    line_ids = fields.One2many('formation.plan.line', 'plan_id', string='Formations', readonly=1,
                               states={'draft': [('readonly', False)]})
    budget = fields.Monetary(compute=_cout_global, string='Budget prévisionnel', currency_field='currency_id')
    budget_real = fields.Monetary(compute=_cout_global, string='Budget réalisé', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Devise',
                                  default=lambda self: self.env.user.company_id.currency_id)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    date = fields.Date('Date établissement', default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    besoin_ids = fields.One2many('formation.besoin', 'plan_id', string='Besoins en formation', readonly=1,
                                 states={'draft': [('readonly', False)]})
    session_ids = fields.One2many('formation.session', 'plan_id', string='Sessions de formation')
    nbr_fiche = fields.Integer(compute=_nbr_fiche, string='Fiches besoin', readonly=1)
    nbr_session = fields.Integer(compute=_nbr_session, string='Sessions de formation', readonly=1)
    state = fields.Selection([('draft', 'Nouveau'),
                              ('done', u'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft', readonly=1)
    actif = fields.Boolean('Recueil de besoin', default=False)

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} - {}".format(record.name, record.objet)))
        return result

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('formation.plan') or '/'
        return super(models.Model, self).create(vals)

    def action_validate(self):
        self.state = 'done'
        self.actif = False

    def action_cancel(self):
        self.state = 'cancel'

    def action_print(self):
        return self.env.ref('r_formation.act_report_besoin_formation').report_action(self)


class FormationPlanLine(models.Model):
    _name = 'formation.plan.line'
    _inherit = ['mail.thread']
    _description = 'Formation du Plan'

    @api.depends('res_ids')
    def _nbr_ressources(self):
        for rec in self:
            rec.res_nbr = len(rec.res_ids)

    @api.depends('date_prev', 'duree')
    def _date_fin(self):
        for rec in self:
            if rec.duree in (0, 1):
                rec.date_fin_prev = rec.date_prev
            else:
                rec.date_fin_prev = rec.date_prev + datetime.timedelta(days=rec.duree)

    @api.depends('session_ids.cout')
    def _budget_reel(self):
        for rec in self:
            rec.cout_real = sum(line.cout for line in rec.session_ids)

    def _get_default_plan(self):
        if self.env.context.get('default_plan_id'):
            return self.env['account.journal'].browse(self.env.context['default_plan_id']).id
        else:
            return None

    name = fields.Char(u'Numéro ', default='/', readonly=1)
    plan_id = fields.Many2one('formation.plan', string='Plan de formation', required=True, readonly=1,
                              states={'draft': [('readonly', False)]}, default=_get_default_plan)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(related='plan_id.currency_id', string='Devise', readonly=1)
    typologie_id = fields.Many2one('formation.typologie', string='Typologie', readonly=1,
                                   states={'draft': [('readonly', False)]})
    theme_id = fields.Many2one('formation.theme', string='Theme', required=True, readonly=1,
                               states={'draft': [('readonly', False)]})
    categorie_id = fields.Many2one(related='theme_id.categorie_id', string='Categorie')
    objectif = fields.Text('Objectif')
    duree = fields.Integer('Durée')
    date_prev = fields.Date('Date previsionnelle ', readonly=1, states={'draft': [('readonly', False)]})
    date_fin_prev = fields.Date(compute=_date_fin, string='Date fin')
    cout_prev = fields.Monetary('Budget prévisionnel', currency_field='currency_id', readonly=1,
                                states={'draft': [('readonly', False)]})
    cout_real = fields.Monetary(compute=_budget_reel, currency_field='currency_id', string=u'Budget réalisé',
                                readonly=1)
    res_nbr = fields.Integer(compute=_nbr_ressources, string='Nombre de ressources', readonly=1)
    res_ids = fields.One2many('formation.plan.line.res', 'plan_line_id', string='Ressources')
    state = fields.Selection(related='plan_id.state', string='Etat', readonly=1)
    session_ids = fields.One2many('formation.session', 'plan_line_id', string='Sessions de formation', readonly=1)

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} - {}".format(record.name, record.theme_id.name)))
        return result

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('formation.plan.line') or '/'
        return super(models.Model, self).create(vals)
    #
    # def unlink(self):
    #     if self.state != 'draft':
    #         raise UserError(_('Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
    #     return super(models.Model, self).unlink()


class FormationPlanLineRessource(models.Model):
    _name = 'formation.plan.line.res'
    _description = 'Ressources de la formation'

    name = fields.Many2one('hr.employee', string='Ressource', required=1, check_company=False)
    job_id = fields.Many2one(related='name.job_id', string='Fonction', readonly=1)
    department_id = fields.Many2one(related='name.department_id', string=u'Département', readonly=1)
    csp_id = fields.Many2one(related='name.csp_id', string=u'CSP', readonly=1)
    plan_line_id = fields.Many2one('formation.plan.line', string='Formation')
