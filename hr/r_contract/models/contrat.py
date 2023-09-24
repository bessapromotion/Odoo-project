# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from datetime import date
from odoo.osv import expression

from odoo.exceptions import ValidationError, _logger

import json
import base64


class Contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    @api.constrains('employee_id', 'state', 'kanban_state', 'date_start', 'date_end')
    def _check_current_contract(self):
        """ Two contracts in state [incoming | open | close] cannot overlap """
        for contract in self.filtered(lambda c: (c.state not in ['draft',
                                                                 'cancel'] or c.state == 'draft' and c.kanban_state == 'done') and c.employee_id):
            domain = [
                ('id', '!=', contract.id),
                ('employee_id', '=', contract.employee_id.id),
                ('company_id', '=', contract.company_id.id),
                '|',
                ('state', 'in', ['open']),
                '&',
                ('state', '=', 'draft'),
                ('kanban_state', '=', 'done')  # replaces incoming
            ]

            if not contract.date_end:
                start_domain = []
                end_domain = ['|', ('date_end', '>=', contract.date_start), ('date_end', '=', False)]
            else:
                start_domain = [('date_start', '<=', contract.date_end)]
                end_domain = ['|', ('date_end', '>', contract.date_start), ('date_end', '=', False)]

            domain = expression.AND([domain, start_domain, end_domain])
            if self.search_count(domain):
                raise ValidationError(
                    _(
                        'An employee can only have one contract at the same time. (Excluding Draft and Cancelled contracts).\n\nEmployee: %(employee_name)s',
                        employee_name=contract.employee_id.name
                    )
                )

    name = fields.Char('Contract Reference', required=True, readonly=1, default='/',
                       states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True,
                                  domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                  check_company=True)
    job_id = fields.Many2one('hr.job', required=True,
                             domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                             string='Job Position')

    date_etablissement = fields.Date('Date etablissement', default=fields.Date.today)
    date_entree = fields.Date(u'Date entrée', default=fields.Date.today)
    nbr_mois = fields.Integer('Durée contrat (en mois)')
    rubrique_ids = fields.One2many('hr.contract.rubrique', 'contract_id', string='Rubriques')
    categorie = fields.Char(u'Catégorie')
    section = fields.Char('Section')

    # periode d'essai
    trial_date_start = fields.Date(string="Date début période d'essai", store=True,
                                   readonly=False)
    trial_nbr_mois = fields.Integer("Durée periode d'essai (en mois)")
    trial_nbr_jours = fields.Integer("Durée periode d'essai (en jours)")
    trial_state = fields.Selection([('open', 'En cours'),
                                    ('renewed', 'Renouvelée'),
                                    ('expired', 'Expirée'),
                                    ('done', 'Clôturée'), ], string='Etat de la période d\'essai', default='open',
                                   readonly=False)
    type_salaire = fields.Selection([('base', 'Salaire de base'),
                                     ('brut', 'Salaire brut'),
                                     ('net', 'Salaire net'), ], string='Type salaire')

    # NEW EDITS
    modele_id = fields.Many2one('hr.contract.modele', string=u'Modèle de contrat', required=True, check_company=True)
    type_id = fields.Many2one('hr.contract.type', related='modele_id.type_id', string='Type de contrat', readonly=True)
    type_id_code = fields.Char(related='type_id.code', readonly=True)  # To be used in the views

    article_lines = fields.One2many('hr.contract.article.line', 'contract_id', string='Articles du contrat',
                                    readonly=False, store=True, copy=True, )  # , compute='_fill_articles'
    num_embauche = fields.Integer('Num Embauche', default=1, readonly=1)
    preavis = fields.Char('Durée préavis')
    uom_preavis = fields.Selection([('jours', 'jours'), ('mois', 'mois')], default='mois')

    # NEW
    dispaly_print_accord = fields.Boolean(default=False)
    notif_pessai = fields.Boolean(default=False)
    notif_contract = fields.Boolean(default=False)

    hr_responsible_id = fields.Many2one('res.users', 'HR Responsible', tracking=True,
                                        default=lambda self: self.env.user,
                                        help='Person responsible for validating the employee\'s contracts.',
                                        required=False)
    type_contract = fields.Selection([('new', 'Nouveau Contrat'), ('rnv', 'Renouvellement de contrat')],
                                     string='Etat du contrat',
                                     default='new', readonly=True)

    def history_contract(self):
        contract = self.env['hr.contract'].search([])
        for rec in contract:
            history = self.env['hr.contract.history'].search([('employee_id', '=', rec.employee_id.id)])
            if history:
                history[0].contract_ids = [(0, 0, {'id': rec.id}), ]

    @api.depends('date_start', 'date_end')
    def get_duree_contract(self):
        for rec in self:
            rec.duree_contrat = 0
            if rec.date_start and rec.date_end:
                rec.duree_contrat = (rec.date_end - rec.date_start)
            rec.date_entree = rec.date_start

    duree_contrat = fields.Char('Durée contrat', compute='get_duree_contract')

    @api.onchange('date_etablissement')
    def onchange_date_etablissement(self):
        if self.date_etablissement:
            self.date_start = self.date_etablissement
            self.date_entree = self.date_etablissement

    @api.onchange('state')
    def _onchange_kanban_state(self):
        if self.state == 'draft':
            self.kanban_state = 'normal'
        elif self.state == 'open':
            self.kanban_state = 'done'
        elif self.state == 'close':
            self.kanban_state = 'blocked'
        elif self.state == 'cancel':
            self.kanban_state = 'blocked'

    @api.onchange('trial_date_start', 'trial_date_end')
    def _onchange_date_trial(self):
        if self.trial_date_start and self.trial_date_end:
            diff = relativedelta(self.trial_date_end, self.trial_date_start)
            self.trial_nbr_mois = diff.years * 12 + diff.months + 1
            self.trial_nbr_jours = diff.days

    @api.onchange('trial_nbr_mois')
    def _onchange_months_trial(self):
        if self.trial_date_start:
            self.trial_date_end = self.trial_date_start + relativedelta(months=self.trial_nbr_mois) - relativedelta(
                days=1)

    def get_trial_date_end(self):
        contracts = self.env['hr.contract'].search([
            ('state', '=', 'open'),
            ('trial_state', '=', 'open'),
            ('notif_pessai', '=', False),
            ('trial_date_end', '=', fields.Date.to_string(date.today()))
        ])
        grp = self.env['res.groups'].search([('name', '=', 'Group HR Menu'), ])
        for rec in contracts:
            rec.trial_state = 'expired'
            for user in grp[0].users:
                self.env['mail.activity'].create({
                    'res_id': rec.id,
                    'user_id': user.id,
                    'res_model_id': self.env['ir.model'].search([('model', '=', 'hr.contract')])[0].id,
                    'res_model': 'r_contract.model_hr_contract',
                    'res_name': rec.name,
                    'activity_type_id': 4,
                    'note': 'Priode d\'essai expirée',
                    'date_deadline': date.today(),
                })
                rec.notif_pessai = True

    @api.onchange('date_start', 'nbr_mois')
    def _onchange_date_contract(self):
        for rc in self:
            if rc.date_start and rc.nbr_mois != 0:  # NEW EDIT
                rc.date_end = rc.date_start + relativedelta(months=+rc.nbr_mois) - relativedelta(days=1)

    @api.onchange('date_start', 'date_end')
    def _onchange_dates_contract(self):
        # print('DEBUG: onchange: date_start—date_end')
        if self.date_start and self.date_end and self.date_end >= self.date_start:
            diff = relativedelta(self.date_end, self.date_start)
            self.nbr_mois = diff.years * 12 + diff.months + 1

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.company_id = self.employee_id.company_id.id
            self.job_id = False
            self.department_id = False
            self.resource_calendar_id = False

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('hr.contract') or '/'
        return super(models.Model, self).create(vals)

    def action_print(self):
        if self.type_id.code == 'CDD':
            self.dispaly_print_accord = True
            return self.env.ref('r_contract.act_report_contrat_cdd').report_action(self)
        else:
            self.dispaly_print_accord = True
            return self.env.ref('r_contract.act_report_contrat_cdi').report_action(self)

    def action_print_accord(self):
        self.dispaly_print_accord = False
        return self.env.ref('r_contract.act_report_accord_confidentialite').report_action(self)

    def action_signer(self):
        self.state = 'open'
        self.env['hr.employee.historique'].create({
            'employe_id': self.employee_id.id,
            'document': 'Contrat de travail',
            'numero': self.name,
            'date_doc': self.date_start,
            'date_prise_effet': self.date_end,
            'user_id': self.user_id.id,
            'note': '',
            'model_name': 'hr.contract',
            'model_id': self.id,
            'num_embauche': self.employee_id.num_embauche,
        })

    @api.constrains('date_end')
    def _check_end_date(self):
        if self.date_end is False and self.type_id.code == 'CDD':
            raise ValidationError("Veuillez saisir la date de fin du contrat.")

    @api.onchange('modele_id')
    def _onchange_modele_id(self):
        if self.modele_id.id is not False:
            # Update the contract type
            self.type_id = self.modele_id.type_id
            # Update date_end & nbr_mois
            if self.type_id.code == 'CDI':
                self.nbr_mois = 0
                self.date_end = False

            # Update articles
            self._fill_articles()

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            self.preavis = self.job_id.preavis
            self.uom_preavis = self.job_id.uom_preavis

    def _fill_articles(self):
        """
        Fill the contract articles with the
        ones beloging to the contract model
        """
        # Do an update on the state 'draft' only
        if self.state != 'draft':
            return

        self.article_lines = False

        # print('DEBUG: Filling articles')
        # Don't update if no contract model is selected
        if self.modele_id.id is False:
            return

        # Clear current articles
        # self.article_ids.unlink()     # Doesn't work
        # self.article_lines = False    # Is set on top so there will be no articles for empty modele_id

        # Get articles of the model (contract.modele)
        article_lines_obj = self.env['hr.contract.modele.article.line']
        article_lines = article_lines_obj.search([('modele_id', '=', self.modele_id.id)])

        # Update the contract articles
        article_ids = []
        # self.article_lines = []
        for line in article_lines:
            # print('DEBUG: Code:', line.code)
            new_obj = {
                'article_id': line.article_id.id,
                'contract_id': self.id,
                'sequence': line.sequence,
            }
            article_ids.append(new_obj)
            # self.article_lines.new(new_obj)

        self.env['hr.contract.article.line'].create(article_ids)

    # @api.onchange('modele_id')
    def motif_id(self):
        c = self.env['hr.contract'].search([('state', '=', 'open')])
        for c in self:
            print(c.modele_id.name)
            for d in c.article_lines:
                d.contract_id = False
            article_lines = self.env['hr.contract.modele.article.line'].search([('modele_id', '=', c.modele_id.id)])
            print(article_lines)
            for line in article_lines:
                print(line.article_id.name)
                self.env['hr.contract.article.line'].create({
                    'article_id': line.article_id.id,
                    'contract_id': c.id,
                    'sequence': line.sequence,
                })

    def get_variables(self):
        # Returns a dictionary of the variable name and its value
        # which will be used in processing articles
        current_state = {
            'civilité': self.employee_id.civilite_id.name or '',
            'affectation': self.employee_id.project_id.name or '',
            'employé': self.employee_id.name or '',
            'durée_periode_essai_mois': self.trial_nbr_mois or 0,
            'durée_periode_essai_jours': self.trial_nbr_jours or 0,
            'durée_periode_essai': '',
            'type_contrat': self.type_id.name or '',
            'company': self.company_id.name or '',
            'date_debut_contrat': self.date_start.strftime("%d/%m/%Y") if self.date_start else '',
            'date_fin_contrat': self.date_end.strftime("%d/%m/%Y") if self.date_end else '',
            'duree_contrat': self.duree_contrat or '',
            'nbr_mois': self.nbr_mois or '',
            'trial_nbr_mois': self.trial_nbr_mois or '',
            'salaire_base': Contract.format_wage(self.wage),
            'poste_travail': self.job_id.name or '',
            # 'durée_préavis':             str(self.job_id.preavis or 0) +' '+ self.job_id.uom_preavis,
            'durée_préavis': str(self.preavis or 0) + ' ' + self.uom_preavis,

            # TO ADD ALL THE NEEDED VARIABLES HERE
            # ...
        }

        # print('DEBUG: fields_state', self.fields_state)
        # Restore the saved state
        """
        if self.state != 'draft' and self.fields_state:
            # print('DEBUG: using saved field states')
            saved_state = json.loads(self.fields_state)
            current_state.update(saved_state)
        """

        current_state['durée_periode_essai'] = Contract.format_period(
            current_state['durée_periode_essai_mois'],
            current_state['durée_periode_essai_jours']
        )

        return current_state

    # H E L P E R
    # F U N C I T O N S

    @staticmethod
    def format_wage(wage, decimal_sep=',', thousand_sep=' '):
        """
        Return a string representation of a date period
        """
        # [[TODO]] Don't make it hard coded
        res = "{:,.2f}".format(round((wage or 0), 2))
        if decimal_sep == thousand_sep:
            return res

        if thousand_sep != ',':
            res = res.replace(',', thousand_sep)
        if decimal_sep != '.':
            res = res.replace('.', decimal_sep)

        return res

    @staticmethod
    def format_period(nb_months, nb_days):
        """
        Return a string representation of a date period
        """
        if nb_months == 0:
            res = str(nb_days) + ' jours'
        else:
            res = str(nb_months) + ' mois'
            if nb_days != 0:
                res += ' et ' + str(nb_days) + ' jours'

        return res


class ContractRubrique(models.Model):
    _name = 'hr.contract.rubrique'
    _description = 'Rubrique'

    name = fields.Char('Rubrique')
    contract_id = fields.Many2one('hr.contract', string='Contrat')
