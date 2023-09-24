# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class FormationEvaluationQuestion(models.Model):
    _name = 'formation.evaluation.question'
    _description = 'Modele de question'

    name = fields.Char('Question')
    code = fields.Integer('code')


class FormationEvaluationNotation(models.Model):
    _name = 'formation.evaluation.notation'
    _description = 'Notations formation'

    name = fields.Many2one('formation.evaluation.question', string='Question')
    code = fields.Integer(related='name.code', string='#')
    insuffisant = fields.Integer('Insuffisant')
    bien = fields.Integer('Bien')
    tres_bien = fields.Integer('Très bien')
    eval_id = fields.Many2one('formation.evaluation', string='Evaluation a chaud')


class FormationEvaluation(models.Model):
    _name = 'formation.evaluation'
    _inherit = ['mail.thread']
    _description = 'Evaluation a chaud'

    @api.depends('eval_ids')
    def _nbr_evaluations(self):
        for rec in self:
            rec.nbr_eval = len(rec.eval_ids)

    @api.depends('note_ids.insuffisant', 'note_ids.bien', 'note_ids.tres_bien')
    def _total_notes(self):
        for rec in self:
            rec.insuffisant = sum(line.insuffisant for line in rec.note_ids)
            rec.bien = sum(line.bien for line in rec.note_ids)
            rec.tres_bien = sum(line.tres_bien for line in rec.note_ids)

    name = fields.Char(u'Numéro ', default='/', readonly=1)
    date = fields.Date('Date', default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    session_id = fields.Many2one('formation.session', string='Session de formation', required=1, readonly=1,
                                 states={'draft': [('readonly', False)]}, ondelete='cascade')
    plan_id = fields.Many2one(related='session_id.plan_id', string='Plan de formation', readonly=1)
    date_debut = fields.Date(related='session_id.date_debut', string='Date de la formation', readonly=1)
    partner_id = fields.Many2one(related='session_id.partner_id', string='Organisme', readonly=1)
    formateur_id = fields.Many2one(related='session_id.formateur_id', string='Formateur', readonly=1)
    comment = fields.Text('Commentaire')
    action = fields.Text('Plan d\'action')
    eval_ids = fields.One2many('formation.evaluation.line', 'eval_id', string='Evaluations individuelles', readonly=1)
    note_ids = fields.One2many('formation.evaluation.notation', 'eval_id', string='Notations', readonly=1)
    nbr_eval = fields.Integer(compute=_nbr_evaluations, string='Nombre evaluations', readonly=1)
    state = fields.Selection([('draft', 'Nouveau'),
                              ('inprogress', 'En cours'),
                              ('done', u'Terminé'),
                              ('cancel', u'Annulé')], string='Etat', default='draft', readonly=1)

    insuffisant = fields.Integer(compute=_total_notes, string='Insuffisant')
    bien = fields.Integer(compute=_total_notes, string='Bien')
    tres_bien = fields.Integer(compute=_total_notes, string='Trés bien')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('formation.evaluation') or '/'

        return super(models.Model, self).create(vals)

    def action_lancer(self):
        self.state = 'inprogress'
        self.note_ids.unlink()
        qst = self.env['formation.evaluation.question'].search([])
        # notes = []
        for line in qst:
            self.env['formation.evaluation.notation'].create({
                'name': line.id,
                'eval_id': self.id,
            })
        # new
        for emp in self.session_id.res_ids:
            self.env['formation.evaluation.line'].create({
                'name': emp.name.id,
                'session_id': self.session_id.id,
                'eval_id': self.id,
            })

    def action_update(self):
        # self.action_lancer()
        for line in self.note_ids:
            line.insuffisant = 0
            line.bien = 0
            line.tres_bien = 0

        for rec in self.eval_ids:
            for line in rec.note_ids:
                i = 0
                b = 0
                t = 0
                if line.note == 'Insuffisant':
                    i = 1
                elif line.note == 'Bien':
                    b = 1
                elif line.note == 'Très bien':
                    t = 1

                eval_rec = self.env['formation.evaluation.notation'].search(
                    [('eval_id', '=', self.id), ('name', '=', line.name.id)])
                if eval_rec.exists():
                    eval_rec.insuffisant += i
                    eval_rec.bien += b
                    eval_rec.tres_bien += t

    def action_validate(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'


class FormationEvaluationLine(models.Model):
    _name = 'formation.evaluation.line'
    _inherit = ['mail.thread']
    _description = 'Evaluation individuelle'

    name = fields.Many2one('hr.employee', string='Apprenant', required=1, readonly=1,
                           states={'draft': [('readonly', False)]}, check_company=False)
    job_id = fields.Many2one(related='name.job_id', string='Fonction', readonly=1)
    image = fields.Binary(related='name.image_1920', string='Photo', readonly=1)
    department_id = fields.Many2one(related='name.department_id', string=u'Département', readonly=1)
    csp_id = fields.Many2one(related='name.csp_id', string=u'CSP', readonly=1)
    eval_id = fields.Many2one('formation.evaluation', string='Evaluation a chaud', readonly=1,
                              states={'draft': [('readonly', False)]}, ondelete='cascade')
    date = fields.Date('Date etablissement', default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    session_id = fields.Many2one(related='eval_id.session_id', string='Formation', readonly=1)
    date_debut = fields.Date(related='eval_id.session_id.date_debut', string='Date formation', readonly=1)
    partner_id = fields.Many2one(related='eval_id.session_id.partner_id', string='Organisme', readonly=1)
    formateur_id = fields.Many2one(related='eval_id.session_id.formateur_id', string='Formateur', readonly=1)

    note_ids = fields.One2many('formation.evaluation.notation.individuelle', 'eval_ind_id', string='Notations')
    state = fields.Selection([('draft', 'Nouveau'),
                              ('done', u'Terminé'),
                              ('cancel', u'Annulé')], string='Etat', default='draft', readonly=1)

    def action_affiche(self):
        self.state = 'done'
        qst = self.env['formation.evaluation.question'].search([])
        # notes = []
        for line in qst:
            self.env['formation.evaluation.notation.individuelle'].create({
                'name': line.id,
                'eval_ind_id': self.id,
                'note': 'Bien',
            })


class FormationEvaluationNotationIndividuelle(models.Model):
    _name = 'formation.evaluation.notation.individuelle'
    _description = 'Notation individuelle'

    name = fields.Many2one('formation.evaluation.question', string='Question', readonly=1)
    code = fields.Integer(related='name.code', string='#', readonly=1)
    note = fields.Selection([('Insuffisant', 'Insuffisant'), ('Bien', 'Bien'), (u'Très bien', u'Très bien')],
                            required=False, string='Note')

    eval_ind_id = fields.Many2one('formation.evaluation.line', string='Evaluation individuelle', ondelete='cascade')
