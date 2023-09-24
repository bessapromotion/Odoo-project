# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
import datetime


class FormationSession(models.Model):
    _name = 'formation.session'
    _inherit = ['mail.thread']
    _description = 'Session de Formation'

    @api.depends('res_ids')
    def _nbr_ressources(self):
        for rec in self:
            rec.res_nbr = len(rec.res_ids)

    @api.depends('eval_ids')
    def _nbr_evaluations(self):
        for rec in self:
            rec.nbr_eval = len(rec.eval_ids)

    @api.depends('date_debut', 'date_fin')
    def compute_duree_formation(self):
        for rec in self:
            rec.duree = 0
            if rec.date_fin and rec.date_debut:
                rec.duree = (rec.date_fin - rec.date_debut).days + 1

    name = fields.Char(u'Numéro ', default='/', readonly=1)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user,
                              states={'done': [('readonly', True)]})
    theme_id = fields.Many2one('formation.theme', string='Theme de la Formation', required=True,
                               states={'done': [('readonly', True)]})
    categorie_id = fields.Many2one(related='theme_id.categorie_id', string='Categorie', readonly=1)
    partner_id = fields.Many2one('res.partner', string='Organisme', states={'done': [('readonly', True)]})
    formateur_id = fields.Many2one('res.partner', string='Formateur', states={'done': [('readonly', True)]})
    type_session = fields.Selection([('intra', 'Intra-entreprise'), ('inter', 'Inter-entreprise')], string='Type',
                                    default='inter', states={'done': [('readonly', True)]})
    lieu = fields.Char('Lieu', states={'done': [('readonly', True)]})
    plan_line_id = fields.Many2one('formation.plan.line', string='Formation', required=True,
                                   states={'done': [('readonly', True)]})
    plan_id = fields.Many2one('formation.plan', string='Plan de formation', states={'done': [('readonly', True)]},required=1, domain="[('state', '=', 'draft'),('actif', '=', True)]")
    currency_id = fields.Many2one(related='plan_line_id.currency_id', string='Devise', readonly=1)
    typologie_id = fields.Many2one(related='plan_line_id.typologie_id', string='Typologie', readonly=1)
    objectif = fields.Text('Objectif', states={'done': [('readonly', True)]})
    duree = fields.Integer('Durée en jour', compute='compute_duree_formation', states={'done': [('readonly', True)]})
    date_debut = fields.Date('Date debut', required=True,
                             states={'done': [('readonly', True)], 'draft': [('required', False)]})
    date_fin = fields.Date('Date fin', required=True,
                           states={'done': [('readonly', True)], 'draft': [('required', False)]})
    cout = fields.Monetary('Cout', currency_field='currency_id')
    res_nbr = fields.Integer(compute=_nbr_ressources, string='Nombre de ressources', readonly=1)
    res_ids = fields.One2many('formation.session.res', 'session_id', string='Ressources',
                              states={'done': [('readonly', True)]})
    eval_ids = fields.One2many('formation.evaluation', 'session_id', string='Evaluations')
    nbr_eval = fields.Integer(compute=_nbr_evaluations, string='Nombre evaluations', readonly=1)

    state = fields.Selection([('draft', 'Nouveau'),
                              ('planned', u'Planifié'),
                              ('done', u'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft', readonly=1)

    @api.onchange('plan_line_id')
    def onchange_plan_line(self):
        self.date_debut = self.plan_line_id.date_prev
        self.theme_id = self.plan_line_id.theme_id.id
        if self.plan_line_id.duree > 0:
            self.date_fin = self.date_debut + datetime.timedelta(days=self.plan_line_id.duree - 1)

        self.res_ids.unlink()
        # req = "delete from formation.session.res where session_id=%s"
        # rub = (self.id,)
        # self._cr.execute(req, rub)

        for rec in self.plan_line_id.res_ids:
            # self.res_ids.unlink()
            self.env['formation.session.res'].create({
                'name': rec.name.id,
                'session_id': self.id,
            })

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('formation.session') or '/'
        return super(models.Model, self).create(vals)

    def unlink(self):
        if any(rec.state != 'draft' for rec in self):
            raise UserError(_('Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))

        return super(models.Model, self).unlink()

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, "{} - {}".format(record.name, record.theme_id.name)))
        return result

    def action_planifier(self):
        self.state = 'planned'

    def action_done(self):
        self.state = 'done'
        for rec in self.res_ids:
            self.env['formation.session.historique'].create({
                'employe_id': rec.name.id,
                'formation_id': self.id,
                'theme_id': self.theme_id.id,
                'formateur_id': self.formateur_id.id,
                'duree': self.duree,
                'date_debut': self.date_debut,
                'date_fin': self.date_fin,
            })

    def action_cancel(self):
        self.state = 'draft'

    def action_print(self):
        return self.env.ref('r_formation.act_report_fiche_presence').report_action(self)


class FormationSessionRessource(models.Model):
    _name = 'formation.session.res'
    _description = 'Ressources de la formation'

    name = fields.Many2one('hr.employee', string='Ressource', required=1, check_company=False)
    job_id = fields.Many2one(related='name.job_id', string='Fonction', readonly=1)
    department_id = fields.Many2one(related='name.department_id', string=u'Département', readonly=1)
    csp_id = fields.Many2one(related='name.csp_id', string=u'CSP', readonly=1)
    session_id = fields.Many2one('formation.session', string='Formation', ondelete='cascade')
    plan_id = fields.Many2one('formation.plan', related='session_id.plan_id', store=True)
