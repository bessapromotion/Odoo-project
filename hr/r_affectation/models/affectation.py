# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError


class Affectation(models.Model):
    _name = 'hr.affectation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Affectation'

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'valid')]

    name = fields.Char('Numero', default='/')
    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=1,
                                 states={'draft': [('readonly', False)]})
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    contract_id = fields.Many2one('hr.contract', string='Contrat', readonly=1, states={'draft': [('readonly', False)]})
    job_id = fields.Many2one(related='contract_id.job_id', string='Fonction', readonly=1)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    project_actuel_id = fields.Many2one('project.project', string='Affectation')
    project_actuel2_id = fields.Many2one(related='project_actuel_id', readonly=1, sotore=True)
    date = fields.Date('Date', required=True, default=datetime.now(), readonly=1,
                       states={'draft': [('readonly', False)]})
    date_effet = fields.Date('Date prise d\'effet', required=True, readonly=1, states={'draft': [('readonly', False)]})
    project_id = fields.Many2one('project.project', required=True, string='Nouvelle affectation', readonly=1,
                                 states={'draft': [('readonly', False)]})
    observation = fields.Text('Observation')
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', 'Validé'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)
    article_lines = fields.One2many('hr.affectation.article.line', 'affectation_id', string='lignes articles')
    article_1_lines = fields.One2many('hr.affectation.article.line', 'affectation_id', string='lignes articles',
                                      domain=[('partie', '=', '1')])
    article_2_lines = fields.One2many('hr.affectation.article.line', 'affectation_id', string='lignes articles',
                                      domain=[('partie', '=', '2')])

    def charger_articles(self):
        self.article_lines.unlink()
        art = self.env['hr.report.modele'].search([('type_id', '=', 'hr.affectation')])
        if art.exists():
            for rec in art.article_lines:
                self.env['hr.affectation.article.line'].create({
                    'article_id': rec.id,
                    'sequence': rec.sequence,
                    'partie': rec.partie,
                    'affectation_id': self.id,
                })

    def get_variables(self):
        # Returns a dictionary of the variable name and its value
        # which will be used in processing articles
        current_state = {
            'civilité': self.employe_id.civilite_id.name or '',
            'société': self.company_id.name or '',
            'type_contrat': self.contract_id.contract_type_id.name or '',
            'date_debut_contrat': self.contract_id.date_start.strftime(
                "%d/%m/%Y") if self.contract_id.date_start else '',
            'date_fin_contrat': self.contract_id.date_end.strftime("%d/%m/%Y") if self.contract_id.date_end else '',
            'poste_travail': self.contract_id.job_id.name or '',
            'employé': self.employe_id.name or '',
            'date_effet': self.date_effet or '',
            'nouvelle_affectation': self.project_id.name or '',

            # TO ADD ALL THE NEEDED VARIABLES HERE
            # ...
        }

        return current_state

    def action_validate(self):
        self.state = 'valid'
        self.name = self.env['ir.sequence'].get('hr.registre') or '/'

        # historique
        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': 'Affectation',
            'numero': self.name,
            'date_doc': self.date,
            'date_prise_effet': self.date_effet,
            'user_id': self.user_id.id,
            # 'state' : self.state,
            'note': 'Affecté(e) à : ' + self.project_id.name,
            'model_name': 'hr.affectation',
            'model_id': self.id,
            'num_embauche': self.employe_id.num_embauche,
        })

    def action_prise_effet(self):
        if self.date_effet <= date.today():
            self.state = 'done'
            self.employe_id.project_id = self.project_id.id
        else:
            raise UserError(_(
                'La date de prise d\'effet n\'est pas encore atteinte, l\'opération n\'est pas autorisée'))

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id:
                rc.project_actuel_id = rc.employe_id.project_id.id or None
                if rc.employe_id.contract_id:
                    rc.contract_id = rc.employe_id.contract_id.id
                else:
                    contracts = self.env['hr.contract'].search([('employee_id', '=', self.employe_id.id),
                                                                ('state', 'not in', ('draft', 'cancel'))])
                    if contracts:
                        rc.contract_id = contracts[0].id
                    else:
                        rc.contract_id = False
                        raise UserError(_("L'employé sélectionné n'a pas de contrat en cours."))
            else:
                rc.contract_id = None
                # rc.project_actuel_id = None

    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        vals['name'] = 'DRAFT/' + str(date.today())[:4]
        return super(models.Model, self).create(vals)

    def action_print_affect(self):
        self.charger_articles()
        return self.env.ref('r_affectation.act_report_affectation').report_action(self)


class AffectationArticleLine(models.Model):
    """
    ArticleLine definition
    List of moveable articles in an employee Contract
    """
    _name = 'hr.affectation.article.line'
    _description = "Ligne d'article dans une affection"
    _order = 'sequence'

    name = fields.Char(related='article_id.name', string='Nom')
    article_id = fields.Many2one('hr.report.modele.article', string='Article',
                                 domain=[('type_id', '=', 'hr.affectation')],
                                 change_default=True)
    # code         = fields.Char(related='article_id.code', string='Code', store=False)
    sequence = fields.Integer(string='Sequence', default=10)
    partie = fields.Selection([('1', 'Partie 1'), ('2', 'Partie 2'), ('3', 'Partie 3')], string='Partie', default='1')

    affectation_id = fields.Many2one('hr.affectation', string='Affectation')
