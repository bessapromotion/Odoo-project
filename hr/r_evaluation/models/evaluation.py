# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class Evaluation(models.Model):
    _name = 'hr.evaluation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Evaluation individuelle'

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
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    job_id = fields.Many2one('hr.job', string='Fonction', readonly=1, states={'draft': [('readonly', False)]})
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    s_date = fields.Date('Date', required=True, default=date.today(), readonly=1,
                         states={'draft': [('readonly', False)]})

    contract_id = fields.Many2one('hr.contract', string='Contrat', required=True, readonly=1,
                                  states={'draft': [('readonly', False)]})
    warning_contract_state = fields.Char(compute=_warning_contract_state, string='Etat du Contrat', readonly=1)
    date_start = fields.Date(related='contract_id.date_start', string=u'Date début', readonly=1)
    date_end = fields.Date(related='contract_id.date_end', string='Date fin', readonly=1)
    date_start_pe = fields.Date(u'Date début', required=True)
    date_end_pe = fields.Date('Date fin', required=True)
    contract_type_id = fields.Many2one(related='contract_id.type_id', string='Cycle de travail', readonly=1)
    type = fields.Selection([('normale', 'Evaluation des compétences'), ('essai', 'Période Essai')],
                            string='Type évaluation', required=1)
    state = fields.Selection([('draft', 'Nouveau'),
                              ('evaluation', 'Evaluation'),
                              ('valid', 'Décision'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')

    # decision
    superviseur_id = fields.Many2one('hr.employee', string='Superviseur de chantier', check_company=True)
    responsable_id = fields.Many2one('hr.employee', string='Responsable hierarchique', check_company=True)
    decision_id = fields.Many2one('hr.evaluation.decision', string=u'Décision')
    decision = fields.Selection(related='decision_id.decision', store=True)
    new_date_frt = fields.Date(u'Date FRT')
    new_duree = fields.Integer('Durée (jour)')
    new_date_debut = fields.Date(u'Date début')
    new_date_fin = fields.Date(u'Date fin')
    new_job_id = fields.Many2one('hr.job', string='Nouveau poste')
    new_salaire = fields.Float('Salaire')

    evaluation_line_ids = fields.One2many('hr.evaluation.line', 'evaluation_id')
    commentaire_sup = fields.Text('Commentaires du supérieu')
    period_ess_juge = fields.Selection([('concluante', 'Concluante'),
                                        ('non_concluante', 'Non concluante'),
                                        ('insuffisante',
                                         'Insuffisante et nécessitant une prorogation pour se prononcer')],
                                       string="Période d’essai jugée")
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company,
                                 readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = 'DRAFT/'
        vals['job_id'] = self.env['hr.employee'].browse(vals.get('employe_id')).job_id.id
        return super(models.Model, self).create(vals)

    def action_validate(self):
        for rec in self.evaluation_line_ids:
            if not rec.evaluation_initial or not rec.evaluation_final:
                raise UserError("Veuillez evaluer le criters : \n - %s" % (rec.criter_id.name))

            self.state = 'valid'
            self.env['hr.employee.historique'].create({
                'employe_id': self.employe_id.id,
                'document': u'Evaluation',
                'numero': self.name,
                'date_doc': date.today(),
                'user_id': self.env.user.id,
                'note': u'Document joint à la fiche d\'evaluation',
                'model_name': 'hr.evaluation',
                'model_id': self.id,
            })

    def action_validate_decision(self):
        self.state = 'done'

    def action_evaluate(self):
        self.state = 'evaluation'
        self.name = self.env['ir.sequence'].get('hr.evaluation') or '/'

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
                # rc.site_id = None
                rc.contract_id = None

    @api.onchange('type')
    def onchange_type(self):
        if self.type == 'essai':
            ctr = self.env['hr.contract'].search(
                [('employee_id', '=', self.employe_id.id), ('type_avenant', '=', 'Contrat')])
            if ctr.exists():
                self.date_start_pe = ctr.trial_date_start
                self.date_end_pe = ctr.trial_date_end
        else:
            self.date_start_pe = self.contract_id.date_start
            self.date_end_pe = self.contract_id.date_end

    def action_cancel(self):
        self.state = 'cancel'

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(
                'Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
        return super(models.Model, self).unlink()

    @api.constrains('date_end_pe', 'type')
    def _check_date(self):
        for record in self:
            if record.type == 'essai':
                if record.date_end_pe < date.today():
                    raise UserError(_(
                        "La periode d'essai a expiré, l'evaluation ne peut se faire que si la période d'essai est encore valide !"))

    def create_frt(self):
        return True

    def create_avenant(self):
        return True

    def action_print(self):
        return self.env.ref('r_evaluation.act_report_fiche_evaluation_individuelle').report_action(self)

    def action_print_vide(self):
        return self.env.ref('r_evaluation.act_report_fiche_evaluation_vierge').report_action(self)


class EvaluationLine(models.Model):
    _name = 'hr.evaluation.line'

    evaluation_id = fields.Many2one('hr.evaluation', string='Evaluation')
    criter_id = fields.Many2one('hr.evaluation.criters', string='Criters', required=True)
    description = fields.Text(related='criter_id.description', string='Description')
    type = fields.Many2many(related='criter_id.type', string='type')
    evaluation_initial = fields.Selection([('1', 'Insuffisant'),
                                           ('2', 'Suffisant'),
                                           ('3', 'PLus que Suffisant')], required=False)
    evaluation_final = fields.Selection([('+', 'Amélioration'),
                                         ('-', 'Régression'),
                                         ('=', 'Constance')], required=False)
