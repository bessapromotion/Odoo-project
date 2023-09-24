# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FRTDecharge(models.Model):
    _name = 'hr.frt.decharge'
    _inherit = ['mail.thread']
    _description = 'Decharge'

    name = fields.Char(u'Numéro', default='/')
    employe_id = fields.Many2one('hr.employee', string='Employé', required=True, check_company=True)
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1, )
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company,
                                 readonly=1)
    job_id = fields.Many2one(related='employe_id.job_id', string='Fonction')
    contract_id = fields.Many2one('hr.contract', string='Contrat', required=True, )
    date_start = fields.Date(related='contract_id.date_start', string=u'Date debut')
    date_end = fields.Date(related='contract_id.date_end', string=u'Date fin')
    type = fields.Selection([('reception', 'RECEPTION'), ('restitution', 'RESTITUTION')], string='Type de décharge',
                            required=True, default='reception')
    decharge_ids = fields.One2many('hr.frt.decharge.line', 'decharge_id')

    @api.onchange('employe_id')
    def onchange_employee(self):
        for rc in self:
            if rc.employe_id:
                if rc.employe_id.contract_id.state == 'open':
                    rc.contract_id = rc.employe_id.contract_id.id
                else:
                    rc.contract_id = False

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('hr.frt.decharge') or '/'
        return super(models.Model, self).create(vals)


class FrtDechargeLine(models.Model):
    _name = 'hr.frt.decharge.line'

    decharge_id = fields.Many2one('hr.frt.decharge', )
    description = fields.Text('Description', required=True, )
    lieu = fields.Text('Lieu', )
    date = fields.Date('Date')
    file = fields.Binary('Fichier')

    def action_print(self):
        return self.env.ref('r_decharge.act_report_decharge').report_action(self)
