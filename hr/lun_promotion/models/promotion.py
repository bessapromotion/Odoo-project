# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError


class Promotion(models.Model):
    _name = 'hr.promotion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Promotion'

    name = fields.Char(u'Numéro', default='/', readonly=1, states={'draft': [('readonly', False)]})

    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=1,
                                 states={'draft': [('readonly', False)]}, check_company=True)
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    job_actuel_id = fields.Many2one('hr.job', string='Fonction', readonly=1)
    date = fields.Date('Date', required=True, default=datetime.now(), readonly=1,
                       states={'draft': [('readonly', False)]})
    date_effet = fields.Date('Date prise d\'effet', required=True, readonly=1, states={'draft': [('readonly', False)]})
    observation = fields.Text('Observation')
    type = fields.Selection([('promotion', 'Promotion'),
                             ('degradation', 'Dégradation'),
                             ('changement', 'Changement de poste')], string='Type changement', required=True)
    job_id = fields.Many2one('hr.job', string='Fonction', required=True, readonly=1,
                             states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', 'Validé'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    company_id = fields.Many2one('res.company', string=u'Société', index=True, readonly=1,
                                 default=lambda self: self.env.company)
    contract_id = fields.Many2one('hr.contract', string='Contrat', required=True, )
    date_start = fields.Date(related='contract_id.date_start', string=u'Date debut')
    date_end = fields.Date(related='contract_id.date_end', string=u'Date fin')
    user_id = fields.Many2one('res.users', string='Etabli par', readonly=1, default=lambda self: self.env.user)
    article_lines = fields.One2many('hr.promotion.article.line', 'promotion_id', string='lignes articles')
    article_1_lines = fields.One2many('hr.promotion.article.line', 'promotion_id', string='lignes articles',
                                      domain=[('partie', '=', '1')])
    article_2_lines = fields.One2many('hr.promotion.article.line', 'promotion_id', string='lignes articles',
                                      domain=[('partie', '=', '2')])

    def charger_articles(self):
        self.article_lines.unlink()
        art = self.env['hr.report.modele'].search([('type_id', '=', 'hr.promotion')])
        if art.exists():
            for rec in art.article_lines:
                self.env['hr.promotion.article.line'].create({
                    'article_id': rec.id,
                    'sequence': rec.sequence,
                    'partie': rec.partie,
                    'promotion_id': self.id,
                })

    def get_variables(self):
        # Returns a dictionary of the variable name and its value
        # which will be used in processing articles
        current_state = {
            'civilité': self.employe_id.civilite_id.name or '',
            'type_contrat': self.contract_id.contract_type_id.name or '',
            'société': self.company_id.name or '',
            'date': self.date.strftime("%d/%m/%Y") or '',
            'date_debut_contrat': self.contract_id.date_start.strftime("%d/%m/%Y") if self.contract_id.date_start else '',
            'date_fin_contrat': self.contract_id.date_end.strftime("%d/%m/%Y") if self.contract_id.date_end else '',
            'poste_travail': self.contract_id.job_id.name or '',
            'employé': self.employe_id.name or '',
            'date_effet': self.date_effet or '',
            'nouvelle_fonction': self.job_id.name or '',

            # TO ADD ALL THE NEEDED VARIABLES HERE
            # ...
        }

        return current_state

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            rc.job_actuel_id = rc.employe_id.job_id.id
            if rc.employe_id.contract_id:
                rc.contract_id = rc.employe_id.contract_id.id
            else:
                contr = self.env['hr.contract'].search([('employee_id', '=', self.employe_id.id),
                                                        ('state', 'not in', ('draft', 'cancel'))])
                if contr:
                    rc.contract_id = contr[0].id
                else:
                    rc.contract_id = None

    def action_validate(self):
        self.state = 'valid'
        self.name = self.env['ir.sequence'].get('hr.confirmation') or '/'
        # historique
        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': 'Changement de poste',
            'numero': self.name,
            'date_doc': self.date,
            'date_prise_effet': self.date_effet,
            'user_id': self.env.user.id,
            # 'state' : self.state,
            'note': '',
            'model_name': 'hr.confirmation',
            'model_id': self.id,
            'num_embauche': self.employe_id.num_embauche,
        })

    def action_prise_effet(self):
        if self.date_effet:
            if self.date_effet <= date.today():
                self.employe_id.job_id = self.job_id.id
            else:
                raise UserError(_(
                    'La date de prise d\'effet n\'est pas encore atteinte, l\'opération n\'est pas autorisée'))

    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):
        vals['name'] = 'DRAFT/' + str(date.today())[:4]
        vals['job_actuel_id'] = self.env['hr.employee'].browse(vals.get('employe_id')).job_id.id
        return super(models.Model, self).create(vals)

    def action_print(self):
        self.charger_articles()
        return self.env.ref('lun_promotion.act_report_promotion').report_action(self)


class PromotionArticleLine(models.Model):
    """
    ArticleLine definition
    List of moveable articles in an employee Contract
    """
    _name = 'hr.promotion.article.line'
    _description = "Ligne d'article dans une promotion"
    _order = 'sequence'

    name = fields.Char(related='article_id.name', string='Nom')
    article_id = fields.Many2one('hr.report.modele.article', string='Article',
                                 domain=[('type_id', '=', 'hr.promotion')],
                                 change_default=True)
    # code         = fields.Char(related='article_id.code', string='Code', store=False)
    sequence = fields.Integer(string='Sequence', default=10)
    partie = fields.Selection([('1', 'Partie 1'), ('2', 'Partie 2'), ('3', 'Partie 3')], string='Partie', default='1')

    promotion_id = fields.Many2one('hr.promotion', string='Promotion')
