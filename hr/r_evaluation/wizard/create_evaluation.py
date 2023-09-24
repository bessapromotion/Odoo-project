# -*- coding: utf-8 -*-
from werkzeug.routing import ValidationError

from odoo import models, fields, api, _
from datetime import date

from odoo.exceptions import UserError


class CreerEvaluationWizard(models.TransientModel):
    _name = 'create.evaluation.wizard'

    def _default_annee(self):
        return str(date.today())[:4]

    def _default_mois(self):
        return str(date.today())[5:7]

    annee      = fields.Char(u'Année', required=True, default=_default_annee)
    mois       = fields.Selection([('01', 'Janvier'), ('02', u'Février'), ('03', 'Mars'), ('04', 'Avril'),
                                   ('05', 'Mai'), ('06', 'Juin'), ('07', 'Juillet'), ('08', 'Aout'),
                                   ('09', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', u'Décembre'), ],
                                  string='Mois', required=True, default=_default_mois)
    user_id    = fields.Many2one('res.users', string='Etabli par', required=1, default=lambda self: self.env.user, readonly=1)
    s_date     = fields.Date('Date', required=True, default=date.today())
    line_ids   = fields.One2many('create.evaluation.wizard.line', 'wiz_id', string='Evaluations')
    state   = fields.Selection([('step1', 'step1'), ('step2', 'step2')], string='Evaluations', default='step1')
    nbr_ctr = fields.Integer('Evaluation fin de contrat', readonly=1)
    nbr_ess = fields.Integer('Evaluation fin période essai', readonly=1)

    def action_recherche(self):
        # fin de contrat
        cntr = self.env['hr.contract'].search([('state', 'in', ('open', 'close')),
                                               ('date_end', '<=', self.annee+'-'+self.mois+'-30'),
                                               ('date_end', '>=', self.annee+'-'+self.mois+'-01')])
        if cntr.exists():
            for rec in cntr:
                rech = self.env['hr.evaluation'].search([('employe_id', '=', rec.employee_id.id),
                                                         ('state', 'not in', ('done', 'cancel'))])
                if rech.exists():
                    exist = True
                else:
                    exist = False
                self.env['create.evaluation.wizard.line'].create({
                    'employe_id' : rec.employee_id.id,
                    'contract_id' : rec.id,
                    'type_evaluation' : 'normale',
                    'date_start_pe' : rec.date_start,
                    'date_end_pe' : rec.date_end,
                    'exist' : exist,
                    'wiz_id' : self.id,
                })
            self.nbr_ctr = len(cntr)

        # fin de contrat
        essai = self.env['hr.contract'].search([('state', 'in', ('open', 'close')),
                                                ('trial_date_end', '<=', self.annee + '-' + self.mois + '-30'),
                                                ('trial_date_end', '>=', self.annee + '-' + self.mois + '-01')])
        if essai.exists():
            for rec in essai:
                if rec.employee_id.job_id.evaluation:
                    rech = self.env['hr.evaluation'].search([('employe_id', '=', rec.employee_id.id),
                                                             ('state', 'not in', ('done', 'cancel'))])
                    if rech.exists():
                        exist = True
                    else:
                        exist = False

                    self.env['create.evaluation.wizard.line'].create({
                        'employe_id' : rec.employee_id.id,
                        'contract_id': rec.id,
                        'type_evaluation': 'essai',
                        'date_start_pe'  : rec.trial_date_start,
                        'date_end_pe': rec.trial_date_end,
                        'exist': exist,
                        'wiz_id'     : self.id,
                    })
            self.nbr_ess = len(essai)

        if self.line_ids:
            self.state = 'step2'
            return {
                'name': _(u'Création des évaluation du mois'),
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_id': self.id,
            }
        else:
            raise UserError(_(u'Aucun contrat ou période d\'essai n\'arrive a échéance pour la période sélectionnée'))

    def action_create(self):
        for rec in self.line_ids:
            if not rec.exist:
                self.env['hr.evaluation'].create({
                    'employe_id' : rec.employe_id.id,
                    'user_id'    : self.user_id.id,
                    'job_id'     : rec.job_id.id,
                    # 'site_id'    : rec.site_id.id,
                    's_date'     : self.s_date,
                    'contract_id'   : rec.contract_id.id,
                    'date_start_pe' : rec.date_start_pe,
                    'date_end_pe'   : rec.date_end_pe,
                    'type'       : rec.type_evaluation,
                    'state'      : 'draft',
                })


class CreerEvaluationWizardLine(models.TransientModel):
    _name = 'create.evaluation.wizard.line'

    employe_id = fields.Many2one('hr.employee', string='Employé', check_company=True)
    # site_id = fields.Many2one(related='employe_id.site_id', string='Fonction')
    job_id = fields.Many2one(related='employe_id.job_id', string='Affectation')
    contract_id = fields.Many2one('hr.contract', string='Contrat')
    regime = fields.Char(related='contract_id.type_id.code', string='Régime')
    # reste = fields.Integer(related='contract_id.delai_expir', string='Exprire dans')
    type_evaluation = fields.Selection([('normale', 'Normale'), ('essai', 'Période Essai')], string='Type évaluation', default='normale')
    date_start_pe  = fields.Date(u'Date début')
    date_end_pe    = fields.Date('Date fin')
    wiz_id = fields.Many2one('create.evaluation.wizard')
    exist  = fields.Boolean(u'A une évaluation en cours')
