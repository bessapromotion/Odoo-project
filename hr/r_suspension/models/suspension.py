# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class Suspension(models.Model):
    _name = 'hr.suspension'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Suspension'

    name = fields.Char(u'Numéro', default='/', readonly=1)

    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=1,
                                 states={'draft': [('readonly', False)]}, check_company=True)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    contract_id = fields.Many2one('hr.contract', string='Contrat', readonly=1, states={'draft': [('readonly', False)]})
    job_id = fields.Many2one(related='contract_id.job_id', string='Fonction', readonly=1)
    s_date = fields.Date('Date', required=True, default=date.today(), readonly=1,
                         states={'draft': [('readonly', False)]})
    duree_susp = fields.Integer(u'Durée de suspension')
    faute_ids = fields.One2many('hr.suspension.faute', 'suspension_id', string='Fautes', required=True, readonly=1,
                                states={'draft': [('readonly', False)]})
    # degre      = fields.Selection(related='motif_id.degre', string='Degré', readonly=1)
    # type_id    = fields.Many2one('hr.sanction.type', string='Est sanctioné par', required=True, readonly=1, states={'draft': [('readonly', False)]})
    date_quest = fields.Date('Date du questionnaire', readonly=1, states={'draft': [('readonly', False)]})
    date_effet = fields.Date('Date prise d\'effet', required=True, readonly=1, states={'draft': [('readonly', False)]})
    restitution_mi = fields.Boolean('Restitution matériels informatique', default=False)
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', 'Validé'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    company_id = fields.Many2one(
        'res.company', 'Société', copy=False,
        required=True, index=True, default=lambda s: s.env.company)

    _sql_constraints = [('constraint_suspension_nb_jours', 'CHECK(duree_susp > 0)',
                         '''La durée de la suspension doit etre supérieure à 0 !''')]

    @api.constrains('duree_susp')
    def _duree_susp(self):
        if self.duree_susp > 20:
            raise UserError(_(u'La durée ne doit pas dépasser les 20 jours!'))
        if self.duree_susp < 0:
            raise UserError(_(u'La durée ne peut pas etre inférieure à 0 !'))

    @api.model
    def create(self, vals):
        vals['name'] = 'DRAFT/' + str(self.s_date)[:4]

        return super(models.Model, self).create(vals)

    def action_validate(self):
        self.state = 'valid'

        num = self.env['ir.sequence'].get('hr.suspension') or '/'
        self.name = num  # + '/' + str(self.s_date)[:4]

        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': u'Suspension',
            'numero': self.name,
            'date_doc': self.s_date,
            'date_prise_effet': self.date_effet,
            'user_id': self.user_id.id,
            'note': 'Suspendu(e) pour ' + str(self.duree_susp) + 'jour(s)',
            'model_name': 'hr.suspension',
            'model_id': self.id,
            'num_embauche': self.employe_id.num_embauche,
        })

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id:
                if rc.employe_id:
                    if rc.employe_id.contract_id:
                        rc.contract_id = rc.employe_id.contract_id.id
                    else:
                        rc.contract_id = self.env['hr.contract'].search([('employee_id', '=', self.employe_id.id),
                                                                         ('state', 'not in', ('draft', 'cancel'))])[
                            0].id
                else:
                    rc.contract_id = None

    def action_prise_effet(self):
        # d1 = datetime.strptime(self.date_effet , '%Y-%m-%d')
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
        if self.state != 'draft':
            raise UserError(_(
                'Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
        self.faute_ids.unlink()
        return super(models.Model, self).unlink()

    def action_print(self):
        return self.env.ref('r_suspension.act_report_decision_suspension').report_action(self)


class SuspensionFaute(models.Model):
    _name = 'hr.suspension.faute'
    _description = 'Faute professionnelle'

    name = fields.Many2one('hr.faute.professionnelle', string='Faute')
    degre = fields.Selection(related='name.degre', string='Degré', readonly=1)
    suspension_id = fields.Many2one('hr.suspension', string='Suspension')
