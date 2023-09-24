# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class Confirmation(models.Model):
    _name = 'hr.confirmation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = u'Décision de confirmation'

    name = fields.Char(u'Numéro', default='/', readonly=1)

    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=1,
                                 states={'draft': [('readonly', False)]}, domain="[('periode', '=', 'essai')]", check_company=True)
    responsable_id = fields.Many2one('hr.employee', string='Responsable', required=True, readonly=1,
                                     states={'draft': [('readonly', False)]}, check_company=True)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    contract_id = fields.Many2one('hr.contract', string='Contrat', readonly=1, states={'draft': [('readonly', False)]})
    job_id = fields.Many2one(related='contract_id.job_id', string='Fonction', readonly=1)
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    s_date = fields.Date('Date', required=True, default=date.today(), readonly=1,
                         states={'draft': [('readonly', False)]})
    feuille_route = fields.Boolean(string='Feuille de route', default=False)
    fr_reference = fields.Char(u'Référence feuille de route')
    fr_date = fields.Date(u'Date feuille de route')
    reference = fields.Char(u'Référence')
    date_effet = fields.Date('Date prise d\'effet', readonly=1, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', 'Validé'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)

    type = fields.Selection([('confirmation', 'Confirmation de poste'),
                             ('prolongation', 'Prolongation peride d\'essai'),
                             ('rupture', 'Periode d\'essai non concluante')], string='Type confirmation',
                            default='confirmation')

    # confirmation poste
    conf_job_id = fields.Many2one('hr.job', string='Fonction', readonly=1, states={'draft': [('readonly', False)]})
    conf_indemnite = fields.Float(u'Indemnité de poste', readonly=1, states={'draft': [('readonly', False)]})

    # prolongation periode essai
    prol_duree = fields.Integer('Prolongée de (mois)', readonly=1, states={'draft': [('readonly', False)]})
    prol_date_fin = fields.Date(u'Date fin', readonly=1, states={'draft': [('readonly', False)]}, default=date.today())

    @api.onchange('contract_id')
    def onchange_contract(self):
        for rc in self:
            # print('DEBUG: trial_date_end: current:', rc.prol_date_fin, 'new:', rc.contract_id.trial_date_end)
            if rc.contract_id.trial_date_end:
                rc.prol_date_fin = rc.contract_id.trial_date_end  # Edited from : date_end to trial_date_end

    @api.onchange('prol_duree')
    def onchange_prol_duree(self):
        for rc in self:
            if rc.prol_date_fin:
                rc.prol_date_fin = rc.prol_date_fin + relativedelta(months=+rc.prol_duree)

    @api.model
    def create(self, vals):
        vals['name'] = 'DRAFT/' + str(date.today())[:4]
        return super(models.Model, self).create(vals)

    def action_validate(self):
        if self.type == 'confirmation':
            self.state = 'valid'
            self.contract_id.trial_state = 'done'
            titre = 'Décision de confirmation'
        else:
            if self.type == 'rupture':
                self.contract_id.state = 'cancel'
                titre = u'Période d\'essai non concluante'
            else:
                titre = u'Renouvellement  période d\'essai'
                self.contract_id.trial_state = 'renewed'
            self.state = 'done'
        self.name = self.env['ir.sequence'].get('hr.confirmation') or '/'

        # historique
        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': titre,
            'numero': self.name,
            'date_doc': self.s_date,
            'date_prise_effet': self.date_effet,
            'user_id': self.user_id.id,
            # 'state' : self.state,
            'note': '',
            'model_name': 'hr.confirmation',
            'model_id': self.id,
            'num_embauche': self.employe_id.num_embauche,
        })

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id:
                # rc.feuille_route = rc.employe_id.feuille_route
                rc.responsable_id = rc.employe_id.parent_id
                if rc.employe_id.contract_id:
                    rc.contract_id = rc.employe_id.contract_id.id
                else:
                    contracts = self.env['hr.contract'].search([('employee_id', '=', self.employe_id.id),
                                                                ('state', 'not in', ('draft', 'cancel'))])
                    if contracts:
                        rc.contract_id = contracts[0].id
                    else:
                        rc.contract_id = False
                        rc.employe_id = False
                        raise UserError(_("L'employé sélectionné n'a pas de contrat en cours."))
            else:
                rc.contract_id = None
                rc.responsable_id = None

    def action_prise_effet(self):
        # d1 = datetime.strptime(self.date_effet , '%Y-%m-%d')
        if self.date_effet:
            if self.date_effet <= date.today():
                self.employe_id.periode = 'confirmé'
                self.state = 'done'
                self.contract_id.trial_state = 'done'
            else:
                raise UserError(_(
                    'La date de prise d\'effet n\'est pas encore atteinte, l\'opération n\'est pas autorisée'))
        else:
            self.employe_id.periode = 'confirmé'
            if self.type == 'rupture':
                self.contract_id.state = 'cancel'
                self.contract_id.trial_state = 'expired'
            self.state = 'done'
            self.contract_id.trial_state = 'done'

    def action_cancel(self):
        self.employe_id.periode = 'essai'
        self.state = 'cancel'

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(
                'Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
        self.employe_id.periode = 'essai'
        return super(models.Model, self).unlink()

    def action_print(self):
        if self.type == 'confirmation':
            return self.env.ref('r_confirmation.act_report_confirmation').report_action(self)
        if self.type == 'prolongation':
            return self.env.ref('r_confirmation.act_report_prolongation').report_action(self)
        if self.type == 'rupture':
            return self.env.ref('r_confirmation.act_report_rupture').report_action(self)


class Hr(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    periode = fields.Selection([('essai', '''Période d'essai'''),
                                ('confirmé', 'Confirmé'),
                                ('frt', 'FRT')], string='Période', default='essai')
