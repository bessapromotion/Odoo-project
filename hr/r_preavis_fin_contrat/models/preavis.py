# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class Preavis(models.Model):
    _name = 'hr.preavis'
    _inherit = ['mail.thread']
    _description = 'Preavis fin de contrat'

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

    name = fields.Char(u'Numéro ', default='/')  # , readonly=1)

    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, readonly=1,
                                 states={'draft': [('readonly', False)]}, check_company=True)
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    job_id = fields.Many2one('hr.job', string='Fonction', readonly=1)
    contract_id = fields.Many2one('hr.contract', string='Contrat', required=True, readonly=1,
                                  states={'draft': [('readonly', False)]})
    warning_contract_state = fields.Char(compute=_warning_contract_state, string='Etat du Contrat', readonly=1)
    date_start = fields.Date(related='contract_id.date_start', string='Date début', readonly=1)
    date_end = fields.Date(related='contract_id.date_end', string='Date fin', readonly=1)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    s_date = fields.Date('Date du préavis', required=True, default=datetime.now(), readonly=1,
                         states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)

    state = fields.Selection([('draft', 'Nouveau'),
                              ('done', 'Terminé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')

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

    def action_validate(self):
        self.name = self.env['ir.sequence'].get('hr.preavis') or '/'
        self.state = 'done'
        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': 'Préavis fin de contrat',
            'numero': self.name,
            'date_doc': self.s_date,
            'date_prise_effet': self.date_end,
            'user_id': self.user_id.id,
            'note': 'Contrat #' + self.contract_id.name,
            'model_name': 'hr.preavis',
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

        return super(models.Model, self).create(vals)

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(
                'Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
        return super(models.Model, self).unlink()

    def action_print(self):
        return self.env.ref('r_preavis_fin_contrat.act_report_preavis_fin_contrat').report_action(self)
