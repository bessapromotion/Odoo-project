# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from odoo.exceptions import UserError
import json


class FRT(models.Model):
    _name = 'hr.frt'
    _inherit = ['mail.thread']
    _description = 'Fin de relation de travail'

    @api.depends('contract_id')
    def _warning_contract_state(self):
        for rec in self:
            if rec.contract_id:
                if rec.contract_id.state == 'close':
                    rec.warning_contract_state = 'Attention ce contrat a expiré !!'
                else:
                    rec.warning_contract_state = ''
            else:
                rec.warning_contract_state = ''

    name = fields.Char(u'Numéro', default='/')  # , readonly=1)

    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=1,
                                 states={'draft': [('readonly', False)]}, check_company=True)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    contract_id = fields.Many2one('hr.contract', string='Contrat', required=True, readonly=1,
                                  states={'draft': [('readonly', False)]})
    warning_contract_state = fields.Char(compute=_warning_contract_state, string='Etat du Contrat', readonly=1)
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    job_id = fields.Many2one('hr.job', string='Fonction', readonly=1)
    s_date = fields.Date('Date document', required=True, default=datetime.now(), readonly=1,
                         states={'draft': [('readonly', False)]})
    reference = fields.Char('Référence')
    date_effet = fields.Date('Date prise effet', readonly=1, required=1, states={'draft': [('readonly', False)]})
    motif_id = fields.Many2one('hr.frt.motif', string='Motif', required=True, readonly=1,
                               states={'draft': [('readonly', False)]})
    code_motif = fields.Char(related='motif_id.code', string='Code motif', readonly=1, store=True)
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', u'Validé'),
                              ('done', u'Terminé'),
                              ('integre', u'Réintegré'),
                              ('cancel', u'Annulé')], string='Etat', default='draft')
    # documents attachés
    med_1_id = fields.Many2one('hr.demeure', string=u'Première mise en demeure')
    med_2_id = fields.Many2one('hr.demeure', string=u'Deuxiéme mise en demeure')
    demission_id = fields.Many2one('hr.demission', string=u'Demission')
    type_fdc = fields.Selection([('sanspreavis', u'Sans préavis'), ('preavis', u'Avec préavis'),
                                 ('nonrenouv', 'Demande de non renouvellement'), ],
                                string='Type de fin', default='sanspreavis', )
    #  readonly=1, states={'draft': [('readonly', False)]})
    preavis_id = fields.Many2one('hr.preavis', string=u'Préavis fin de contrat')
    # evaluation_id = fields.Many2one('hr.evaluation', string=u'Evaluation')
    evaluation_id = fields.Many2one('hr.evaluation', string=u'Evaluation')
    date_debut_abs = fields.Date(related='med_1_id.date_debut_abscence', string='Date absence')
    date_demission = fields.Date(related='demission_id.date_demission', string=u'Date de démission')
    date_reception = fields.Date(related='demission_id.date_reception', string=u'Date de réception')
    date_start = fields.Date(related='contract_id.date_start', string=u'Date debut')
    date_end = fields.Date(related='contract_id.date_end', string=u'Date fin')
    dem_renouv = fields.Char('Demande de renouvellement de Mr.')
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)
    # article_lines = fields.One2many('hr.frt.article.line', 'frt_id',
    #                                 string='Articles du contrat', )  # , compute='_fill_articles'

    article_lines = fields.One2many('hr.frt.article.line', 'frt_id', string='lignes articles')
    article_1_domain_lines = fields.One2many('hr.frt.article.line', 'frt_id', string='lignes 1 articles', )
    article_1_lines = fields.One2many('hr.frt.article.line', 'frt_id', string='lignes 1 articles',
                                      domain=lambda self: [("code", "=", self.code_motif), ('partie', '=', '1')], )
    article_2_lines = fields.One2many('hr.frt.article.line', 'frt_id', string='lignes 2 articles',
                                      domain=lambda self: [("code", "=", self.code_motif), ('partie', '=', '2')], )

    def charger_articles(self):
        self.article_lines.unlink()
        art = self.env['hr.report.modele'].search([('type_id', '=', 'hr.frt')])
        if art.exists():
            for rec in art.article_lines:
                a = self.env['hr.frt.article.line'].create({
                    'article_id': rec.id,
                    'sequence': rec.sequence,
                    'partie': rec.partie,
                    'code': rec.code,
                    'frt_id': self.id,
                })

    def get_variables(self):
        current_state = {
            'civilité': self.employe_id.civilite_id.name or '',
            'employé': self.employe_id.name or '',
            'motif': self.motif_id.name or '',
            'contrat': self.contract_id.name or '',
            'poste_travail': self.contract_id.job_id.name or '',
            'date_effet': str(self.date_effet.day) + '/' + str(self.date_effet.month) + '/' + str(
                self.date_effet.year) or '',
            'société': self.company_id.name or '',
            'type_contrat': self.contract_id.type_id.name or '',
            'date_debut_contrat': self.contract_id.date_start.strftime(
                "%d/%m/%Y") if self.contract_id.date_start else '',
            'date_fin_contrat': self.contract_id.date_end.strftime("%d/%m/%Y") if self.contract_id.date_end else '',
            'date': self.s_date.strftime("%d/%m/%Y") if self.s_date else '',
            'date_de_la_première_mise_en_demeure': self.med_1_id.s_date.strftime(
                "%d/%m/%Y") if self.med_1_id.s_date else '',
            'date_de_la_deuxième_mise_en_demeure': self.med_2_id.s_date.strftime(
                "%d/%m/%Y") if self.med_2_id.s_date else '',
            'référence_de_la_première_mise_en_demeure': self.med_1_id.name,
            'référence_de_la_première_mise_en_demeure ': self.med_2_id.name,

        }
        return current_state

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id:
                rc.job_id = rc.employe_id.job_id.id
                if rc.employe_id.contract_id.state == 'open':
                    rc.contract_id = rc.employe_id.contract_id.id
                else:
                    rc.contract_id = None
            else:
                rc.job_id = None
                rc.contract_id = None
            rc.med_1_id = False
            rc.med_2_id = False

    @api.onchange('med_1_id')
    def onchange_med_1(self):
        for rc in self:
            if rc.med_1_id:
                rc.med_2_id = self.env['hr.demeure'].search([('first_med', '=', rc.med_1_id.id)]).id

    def action_validate(self):
        self.state = 'valid'
        self.name = self.env['ir.sequence'].get('hr.frt') or '/'
        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': 'Décision de fin de relation de travail',
            'numero': self.name,
            'date_doc': self.s_date,
            'date_prise_effet': self.date_effet,
            'user_id': self.user_id.id,
            'note': 'Motif -> ' + self.motif_id.name,
            'model_name': 'hr.frt',
            'model_id': self.id,
            'num_embauche': self.employe_id.num_embauche,
        })

    @api.constrains('date_effet', 'date_end')
    def _check_date(self):
        for record in self:
            if record.motif_id.cntrl_date and record.contract_id.date_end:
                if record.date_effet >= record.contract_id.date_end:
                    raise UserError(_(
                        "La date de prise d'effet ne peut pas etre inférieure à la date de la fin du contrat ou l'avenant !"))

    def action_prise_effet(self):
        if self.date_effet <= date.today():
            self.state = 'done'
            # self.contract_id.date_fin_effective = self.date_effet - relativedelta(days=1)
            self.contract_id.date_end = self.date_effet
            self.contract_id.state = 'cancel'

            self.employe_id.active = False
        else:
            raise UserError(_(
                'La date de prise d\'effet n\'est pas encore atteinte, l\'opération n\'est pas autorisée'))

    def action_cancel(self):
        self.state = 'cancel'

    def action_print(self):
        self.charger_articles()
        return self.env.ref('r_frt.act_report_decision_fin_relation_travail').report_action(self)

    @api.model
    def create(self, vals):
        self.employe_id.etat_frt = self.state
        if vals.get('name', '/') == '/':
            vals['name'] = 'DRAFT'

        vals['job_id'] = self.env['hr.employee'].browse(vals.get('employe_id')).job_id.id

        return super(models.Model, self).create(vals)

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(
                'Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
        return super(models.Model, self).unlink()


class FrtArticleLine(models.Model):
    _name = 'hr.frt.article.line'
    _description = "Ligne d'article dans une FRT"
    _order = 'sequence'

    name = fields.Char(related='article_id.name', string='Nom')
    article_id = fields.Many2one('hr.report.modele.article', string='Article',
                                 domain=[('type_id', '=', 'hr.affectation')],
                                 change_default=True)
    code = fields.Char(related='article_id.code', string='Code', store=False)
    sequence = fields.Integer(string='Sequence', default=10)
    partie = fields.Selection([('1', 'Partie 1'), ('2', 'Partie 2'), ('3', 'Partie 3')], string='Partie', default='1')

    frt_id = fields.Many2one('hr.frt', string='FRT')


class Hr(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    en_frt = fields.Boolean('En FRT', default=False)
    etat_frt = fields.Char(string='Etat FRT')
