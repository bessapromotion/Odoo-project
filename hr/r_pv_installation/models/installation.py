# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.tools import conversion
from odoo.exceptions import UserError


class PvInstallation(models.Model):
    _name = 'hr.installation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'PV Installation'

    @api.depends('s_date')
    def _annee_lettre(self):
        for rec in self:
            an = float(str(rec.s_date)[:4])
            rec.annee_lettre = conversion.conversion(an)[:-7]

    def pv_all(self):
        contrats = self.env['hr.contract'].search(
            [('hr_instalation_id', '=', False), ('state', '=', 'open')])
        for rec in contrats:
            instalation_id = self.env['hr.installation'].create({
                'employe_id': rec.employee_id.id,
                'contract_id': rec.id,
                'company_id': rec.company_id.id,
                'installation_date': date.today(),
            })
            instalation_id.action_validate()
            rec.hr_instalation_id = instalation_id.id

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
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    contract_id = fields.Many2one('hr.contract', string='Contrat', required=1, readonly=1,
                                  states={'draft': [('readonly', False)]})
    warning_contract_state = fields.Char(compute=_warning_contract_state, string='Etat du Contrat', readonly=1)
    job_id = fields.Many2one('hr.job', string='Fonction', readonly=1, states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string='Direction', readonly=1,
                                    states={'draft': [('readonly', False)]})
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    s_date = fields.Date('Date document', required=True, default=date.today(), readonly=1,
                         states={'draft': [('readonly', False)]})
    installation_date = fields.Date('Date installation', required=True, readonly=1,
                                    states={'draft': [('readonly', False)]})
    annee_lettre = fields.Char(compute=_annee_lettre)
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)

    state = fields.Selection([('draft', 'Nouveau'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id:
                rc.job_id = rc.employe_id.job_id.id
                rc.department_id = rc.employe_id.department_id.id
                if rc.employe_id.contract_id.state == 'open':
                    rc.contract_id = rc.employe_id.contract_id.id
                    rc.installation_date = rc.employe_id.contract_id.date_start
                else:
                    rc.contract_id = None
                    rc.installation_date = None

            else:
                rc.job_id = None
                rc.department_id = None
                rc.contract_id = None
                rc.installation_date = None

    def action_validate(self):
        hr_installation_id = self.env['hr.installation'].search(
            [('employe_id', '=', self.employe_id.id), ('contract_id', '=', self.contract_id.id),
             ('company_id', '=', self.company_id.id), ('state', '=', 'done')])
        if hr_installation_id:
            raise UserError(_('Il existe deja un pv d\'instalation.'))
        self.state = 'done'
        self.name = self.env['ir.sequence'].get('hr.installation') or '/'
        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': 'PV Installation ',
            'numero': self.name,
            'date_doc': self.s_date,
            # 'date_prise_effet' : self.date_effet,
            'user_id': self.user_id.id,
            'note': 'Poste -> ' + self.job_id.name,
            'model_name': 'hr.installation',
            'model_id': self.id,
            'num_embauche': self.employe_id.num_embauche,
        })

    def action_cancel(self):
        self.state = 'cancel'

    @api.model
    def create(self, vals):

        if vals.get('name', '/') == '/':
            vals['name'] = 'DRAFT'

        vals['job_id'] = self.env['hr.employee'].browse(vals.get('employe_id')).job_id.id
        vals['department_id'] = self.env['hr.employee'].browse(vals.get('employe_id')).department_id.id

        return super(models.Model, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_(
                    'Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
            return super(models.Model, self).unlink()

    def action_print(self):
        return self.env.ref('r_pv_installation.act_report_pv_installation_rh').report_action(self)
