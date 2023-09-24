# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError


class Questionnaire(models.Model):
    _name = 'hr.questionnaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Questionnaire'

    @api.constrains('faute_ids')
    def _check_faute_ids(self):
        for rec in self:
            if len(rec.faute_ids) > 1:
                raise ValidationError("Il ne peut y avoir qu'une seule faute par questionnaire.")

    @api.depends('faute_ids')
    def _compute_faute_degree(self):
        for rec in self:
            if rec.faute_ids:
                rec.faute_degree = rec.faute_ids[0].degre
            else:
                rec.faute_degree = False

    name = fields.Char(u'Numéro', default='/', readonly=1)

    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=1,
                                 states={'draft': [('readonly', False)], 'progress': [('readonly', False)]},
                                 check_company=True)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)], 'progress': [('readonly', False)]})
    resp_commission_id = fields.Many2one('hr.employee', string='Responsable commission', readonly=1,
                                         states={'draft': [('readonly', False)], 'progress': [('readonly', False)]},
                                         check_company=True)
    resp_hierarchique_id = fields.Many2one('hr.employee', string='Responsable hierarchique', readonly=1,
                                           states={'draft': [('readonly', False)], 'progress': [('readonly', False)]},
                                           check_company=True)
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    contract_id = fields.Many2one('hr.contract', string='Contrat', readonly=1,
                                  states={'draft': [('readonly', False)], 'progress': [('readonly', False)]})
    job_id = fields.Many2one(related='contract_id.job_id', string='Fonction', readonly=1)
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    s_date = fields.Date('Date du questionnaire', required=True, default=date.today(), readonly=1,
                         states={'draft': [('readonly', False)], 'progress': [('readonly', False)]})
    reponse = fields.Text('Reponse du concerné', readonly=1,
                          states={'draft': [('readonly', False)], 'progress': [('readonly', False)]})
    reponse_date = fields.Date(string='Date de réponse', readonly=1,
                               states={'draft': [('readonly', False)], 'progress': [('readonly', False)]})
    observation_resp = fields.Text('Observations', readonly=1,
                                   states={'draft': [('readonly', False)], 'progress': [('readonly', False)]})
    question = fields.Text('Question', readonly=1,
                           states={'draft': [('readonly', False)], 'progress': [('readonly', False)]})
    # decision_drh = fields.Text('Decisions', readonly=1, states={'draft': [('readonly', False)], 'progress': [('readonly', False)]})
    decision_drh = fields.Many2one('hr.sanction.type', readonly=1,
                                   states={'draft': [('readonly', False)], 'progress': [('readonly', False)]},
                                   domain="[('degre', '=', faute_degree)]")
    faute_ids = fields.One2many('hr.questionnaire.faute', 'questionnaire_id', string='Fautes', required=True,
                                readonly=1, states={'draft': [('readonly', False)], 'progress': [('readonly', False)]})
    faute_degree = fields.Char(compute="_compute_faute_degree", store=True)
    state = fields.Selection([('draft', 'Nouveau'),
                              ('progress', 'En cours'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    company_id = fields.Many2one(
        'res.company', 'Company', copy=False,
        required=True, index=True, default=lambda s: s.env.company)

    @api.model
    def create(self, vals):
        vals['name'] = 'DRAFT/' + str(date.today())[:4]
        return super(models.Model, self).create(vals)

    def action_validate(self):
        if len(self.faute_ids) == 0:
            raise UserError(_(
                'Veuillez saisir la liste des fautes professionnelles comises'))

        else:
            self.state = 'progress'
            self.name = self.env['ir.sequence'].get('hr.questionnaire') or '/'
            self.env['hr.employee.historique'].create({
                'employe_id': self.employe_id.id,
                'document': 'Questionnaire disciplinaire',
                'numero': self.name,
                'date_doc': self.s_date,
                'date_prise_effet': None,
                'user_id': self.user_id.id,
                'note': ' ',
                'model_name': 'hr.questionnaire',
                'model_id': self.id,
                'num_embauche': self.employe_id.num_embauche,
            })

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id:
                rc.resp_hierarchique_id = rc.employe_id.parent_id.id
                if rc.employe_id.contract_id:
                    rc.contract_id = rc.employe_id.contract_id.id
                else:
                    contr = self.env['hr.contract'].search([('employee_id', '=', self.employe_id.id),
                                                            ('state', 'not in', ('draft', 'cancel'))])
                    if contr:
                        rc.contract_id = contr[0].id
                    else:
                        rc.contract_id = None
            else:
                rc.contract_id = None
                rc.resp_hierarchique_id = None

    @api.onchange('reponse')
    def _onchange_reponse(self):
        for rec in self:
            if rec.reponse:
                rec.reponse_date = fields.Date.today()

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(
                'Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
        return super(models.Model, self).unlink()

    def action_print(self):
        return self.env.ref('r_questionnaire.act_report_questionnaire').report_action(self)

    def action_print_vide(self):
        return self.env.ref('r_questionnaire.act_report_questionnaire_vide').report_action(self)


class QuestionnaireFaute(models.Model):
    _name = 'hr.questionnaire.faute'
    _description = 'Faute professionnelle'

    name = fields.Many2one('hr.faute.professionnelle', required=True, string='Faute')
    degre = fields.Selection(related='name.degre', string='Degré', readonly=1)
    description = fields.Char('Description')
    questionnaire_id = fields.Many2one('hr.questionnaire', string='Questionnaire')
    date_faute = fields.Date(string="Date de la faute", required=True)

    @api.onchange('name')
    def onchange_faute(self):
        for rec in self:
            if rec.name:
                rec.description = rec.name.name

    # _sql_constraints = [
    #     ('Unique fault', 'unique(name,questionnaire_id)', 'Il existe une faute professionnelle en double'),
    #     ]
