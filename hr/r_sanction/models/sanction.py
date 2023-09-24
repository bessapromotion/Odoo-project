# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class Sanction(models.Model):
    _name = 'hr.sanction'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Décision disciplinaire'

    @api.constrains("date_effet", "date_faute")
    def _check_date_effet_faute(self):
        for rec in self:
            if rec.date_effet and rec.date_faute and rec.date_effet < rec.date_faute:
                raise UserError("La date d'effet doit être postérieure a la date de la faute.")

    company_id = fields.Many2one('res.company', string=u'Société', index=True, readonly=1,
                                 default=lambda self: self.env.company)
    name = fields.Char(u'Numéro', default='/', readonly=1)
    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=1,
                                 states={'draft': [('readonly', False)]}, check_company=True)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    contract_id = fields.Many2one('hr.contract', string='Contrat', readonly=1, states={'draft': [('readonly', False)]})
    job_id = fields.Many2one(related='contract_id.job_id', string='Fonction', readonly=1)
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    s_date = fields.Date('Date', required=True, default=date.today(), readonly=1,
                         states={'draft': [('readonly', False)]})
    reference = fields.Char(u'Référence')
    motif_id = fields.Many2one('hr.faute.professionnelle', string='Motif', compute="_compute_motif_id")
    degre = fields.Selection(related='motif_id.degre', string='Degré')
    type_id = fields.Many2one('hr.sanction.type', string='Est sanctioné par', compute="_compute_motif_id")
    # questionnaire_id = fields.Many2one('hr.questionnaire', string='Questionnaire', readonly=1, states={'draft': [('readonly', False)]})
    questionnaire_id = fields.Many2one('hr.questionnaire', string='Questionnaire', readonly=1,
                                       states={'draft': [('readonly', False)]},
                                       domain="[('employe_id', '=', employe_id)]")
    date_quest = fields.Date(related='questionnaire_id.s_date',
                             string='Date du questionnaire')  # , readonly=1, states={'draft': [('readonly', False)]})
    date_faute = fields.Date('Date de la faute', compute="_compute_motif_id")
    date_effet = fields.Date('Date prise d\'effet', required=True, readonly=1, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', 'Validé'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    article_lines = fields.One2many('hr.sanction.article.line', 'sanction_id', string='lignes articles')
    article_mise_1_lines = fields.One2many('hr.sanction.article.line', 'sanction_id', string='lignes articles',
                                           domain=[('partie', '=', '1'), ('code', '=', 'mise_pied_1')])
    article_mise_2_lines = fields.One2many('hr.sanction.article.line', 'sanction_id', string='lignes articles',
                                           domain=[('partie', '=', '2'), ('code', '=', 'mise_pied_2')])
    article_sanction_1_lines = fields.One2many('hr.sanction.article.line', 'sanction_id', string='lignes articles',
                                               domain=[('partie', '=', '1'), ('code', '=', 'sanction_1')])
    article_sanction_2_lines = fields.One2many('hr.sanction.article.line', 'sanction_id', string='lignes articles',
                                               domain=[('partie', '=', '2'), ('code', '=', 'sanction_2')])
    article_avertissement_1_lines = fields.One2many('hr.sanction.article.line', 'sanction_id', string='lignes articles',
                                                    domain=[('partie', '=', '1'), ('code', '=', 'avertissement_1')])
    article_avertissement_2_lines = fields.One2many('hr.sanction.article.line', 'sanction_id', string='lignes articles',
                                                    domain=[('partie', '=', '2'), ('code', '=', 'avertissement_2')])

    @api.depends('questionnaire_id')
    def _compute_motif_id(self):
        for rec in self:
            if rec.questionnaire_id:
                rec.motif_id = rec.questionnaire_id.faute_ids[0].name.id
                rec.date_faute = rec.questionnaire_id.faute_ids[0].date_faute
                rec.type_id = rec.questionnaire_id.decision_drh.id
            else:
                rec.motif_id = False
                rec.date_faute = False
                rec.type_id = False

    @api.model
    def create(self, vals):
        vals['name'] = 'DRAFT/' + str(date.today())[:4]
        return super(models.Model, self).create(vals)

    def charger_articles(self):
        self.article_lines.unlink()
        art = self.env['hr.report.modele'].search([('type_id', '=', 'hr.sanction')])
        if art.exists():
            for rec in art.article_lines:
                self.env['hr.sanction.article.line'].create({
                    'article_id': rec.id,
                    'sequence': rec.sequence,
                    'partie': rec.partie,
                    'code': rec.code,
                    'sanction_id': self.id,
                })

    def action_validate(self):
        self.state = 'valid'
        self.name = self.env['ir.sequence'].get('hr.sanction') or '/'
        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': u'Décision disciplinaire',
            'numero': self.name,
            'date_doc': self.s_date,
            'date_prise_effet': self.date_effet,
            'user_id': self.user_id.id,
            'note': self.type_id.name or '',
            'model_name': 'hr.sanction',
            'model_id': self.id,
            'num_embauche': self.employe_id.num_embauche,
        })

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id:
                if rc.employe_id.contract_id:
                    rc.contract_id = rc.employe_id.contract_id.id
                else:
                    try:
                        rc.contract_id = self.env['hr.contract'].search([('employee_id', '=', self.employe_id.id),
                                                                         ('state', 'not in', ('draft', 'cancel'))])[
                            0].id
                    except:
                        rc.contract_id = False
            else:
                rc.contract_id = False

    #    @api.onchange('questionnaire_id')
    #    def onchange_questionnaire(self):
    #        for rec in self:
    #            if rec.questionnaire_id:
    #                rec.date_quest = rec.questionnaire_id.s_date
    #            else:
    #                rec.date_quest = None

    # @api.onchange('motif_id')
    # def onchange_motif(self):
    #     for rc in self:
    #         if rc.motif_id:
    #             types = self.env['hr.sanction.type'].search([('degre', '=', rc.motif_id.degre)])
    #             if len(types) == 1:
    #                 rc.type_id = types[0].id
    #             else:
    #                 rc.type_id = None

    def action_prise_effet(self):
        # d1 = datetime.strptime(self.date_effet , '%Y-%m-%d')
        self.charger_articles()
        if self.date_effet:
            if self.date_effet <= date.today():
                self.state = 'done'
            else:
                raise UserError(_(
                    'La date de prise d\'effet n\'est pas encore atteinte, l\'opération n\'est pas autorisée'))
        else:
            self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def unlink(self):
        if any(rec.state != 'draft' for rec in self):
            raise UserError(
                _(
                    u'Suppression non autorisée ! \n\n  Vous ne pouvez pas supprimer un document déjà validé ! \n\n Veuillez contacter l\'administrateur'))
        return super(models.Model, self).unlink()

    def action_print(self):
        self.charger_articles()
        return self.env.ref('r_sanction.act_report_sanction').report_action(self)

    # impression du rapport
    def get_variables(self):
        # Returns a dictionary of the variable name and its value
        # which will be used in processing articles
        if self.degre:
            if self.degre == '1':
                dgr = '1er degré'
            elif self.degre == '2':
                dgr = '2eme degré'
            else:
                dgr = '3eme degré'
        else:
            dgr = ''

        current_state = {
            'civilité': self.employe_id.civilite_id.name or '',
            'société': self.company_id.name,
            'statut_date': '',
            'statut_date_maj': '',
            'date_nomination_drh': '',
            'nom_drh': '',
            'drh_nom_fonction': '',
            'numero_contrat': self.contract_id.name or '',
            'date_debut_contrat': self.contract_id.date_start.strftime(
                "%d/%m/%Y") if self.contract_id.date_start else '',
            'date_fin_contrat': self.contract_id.date_end.strftime("%d/%m/%Y") if self.contract_id.date_end else '',
            'employé': self.employe_id.name or '',
            'fonction': self.job_id.name or '',
            'motif': self.motif_id.name or '',
            'date_faute': self.date_faute.strftime("%d/%m/%Y") if self.date_faute else '',
            'date_questionnaire': self.questionnaire_id.s_date.strftime(
                "%d/%m/%Y") if self.questionnaire_id.s_date else '',
            'decision_questionnaire': self.questionnaire_id.decision_drh.name if self.questionnaire_id.decision_drh else '',
            'type_contrat': self.type_id.name or '',
            'sanction': self.type_id.name or '',
            'date_effet': self.date_effet.strftime("%d/%m/%Y") if self.date_effet else '',
            'faute_degre': dgr,

            # TO ADD ALL THE NEEDED VARIABLES HERE
            # ...
        }

        return current_state


class SanctionArticleLine(models.Model):
    """
    ArticleLine definition
    List of moveable articles in an employee Contract
    """
    _name = 'hr.sanction.article.line'
    _description = "Ligne d'article dans une sanction"
    _order = 'sequence'

    name = fields.Char(related='article_id.name', string='Nom')
    article_id = fields.Many2one('hr.report.modele.article', string='Article', domain=[('type_id', '=', 'hr.sanction')],
                                 change_default=True)
    code = fields.Char(related='article_id.code', string='Code', store=True)
    sequence = fields.Integer(string='Sequence', default=10)
    partie = fields.Selection([('1', 'Partie 1'), ('2', 'Partie 2'), ('3', 'Partie 3')], string='Partie', default='1')

    sanction_id = fields.Many2one('hr.sanction', string='Sanction')
