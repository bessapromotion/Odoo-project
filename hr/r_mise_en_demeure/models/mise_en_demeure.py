# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class MiseEnDemeure(models.Model):
    _name = 'hr.demeure'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Mise en demeure'

    @api.constrains('s_date', 'first_med', 'first_med_date', 'date_debut_abscence', 'numero')
    def _check_date_2med(self):
        for rec in self:
            if rec.numero == '2':
                if rec.first_med and (rec.s_date - rec.first_med.s_date).days < 2:
                    raise UserError(
                        "Impossible de saisir une deuxième mise en demeure qu'aprés 48 heures de la date de la première mise en demeure.")
            elif rec.numero == '1':
                if (rec.s_date - rec.date_debut_abscence).days < 2:
                    raise UserError(
                        "La date d'absence doit être antérieure à la date d'établissement de la 1ère mise en demeure d'au moins 48h.")

    def _default_motif(self):
        motif = self.env['hr.demeure.motif'].search([], limit=1)
        if motif.exists():
            return motif.id
        else:
            return None

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
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1,
                              states={'draft': [('readonly', False)]})
    image = fields.Binary(related='employe_id.image_1920', string='Photo')
    numero = fields.Selection([('1', '1ere mise en demeure'), ('2', '2eme mise en demeure')], string='Type MED',
                              default='1')
    # first_med  = fields.Many2one('hr.demeure', string='Première Mise en demeure', domain="[('employe_id', '=', employe_id)]")
    first_med = fields.Many2one('hr.demeure', string='Première Mise en demeure', compute="_compute_first_med",
                                store=True)
    first_med_date = fields.Date(related='first_med.s_date', string='Du')
    matricule = fields.Char(related='employe_id.matricule', string='Matricule')
    job_id = fields.Many2one('hr.job', string='Fonction', readonly=1)
    contract_id = fields.Many2one('hr.contract', string='Contrat', required=True, readonly=1,
                                  states={'draft': [('readonly', False)]})
    warning_contract_state = fields.Char(compute=_warning_contract_state, string='Etat du Contrat', readonly=1)

    s_date = fields.Date('Date', required=True, default=datetime.now(), readonly=1,
                         states={'draft': [('readonly', False)]})
    motif_id = fields.Many2one('hr.demeure.motif', string='Motif', required=True, default=_default_motif, readonly=1,
                               states={'draft': [('readonly', False)]})
    description_motif = fields.Char(string='Description Motif', required=False, readonly=1,
                                    states={'draft': [('readonly', False)]})
    date_debut_abscence = fields.Date('Date debut abscence', required=True, readonly=1,
                                      states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)
    state = fields.Selection([('draft', 'Nouveau'),
                              ('done', 'Validé'),
                              ('archived', 'Archivé'),
                              ('cancel', 'Annulé')], string='Etat', default='draft')
    note = fields.Char(readonly=True)

    @api.depends('employe_id', 'state')
    def _compute_first_med(self):
        for rec in self:
            valid_first_med = self.env['hr.demeure'].search(
                [('employe_id', '=', rec.employe_id.id), ('numero', '=', '1'), ('state', '=', 'done')]).filtered(
                lambda rec: not isinstance(rec.id, models.NewId))
            valid_sec_med = self.env['hr.demeure'].search(
                [('employe_id', '=', rec.employe_id.id), ('numero', '=', '2'), ('state', '=', 'done')]).filtered(
                lambda rec: not isinstance(rec.id, models.NewId))
            if len(valid_first_med) > 1:
                raise UserError(
                    "L'employe(é) {} posséde plusieurs 1éres demeures. Veuillez archivez les mises en demeures expirées.".format(
                        rec.employe_id.name))
            if len(valid_sec_med) > 1:
                raise UserError(
                    "L'employe(é) {} posséde plusieurs 2émes demeures. Veuillez archivez les mises en demeures expirées.".format(
                        rec.employe_id.name))

            if valid_first_med and valid_first_med.id != rec.id and not valid_sec_med:
                rec.numero = '2'
                rec.first_med = valid_first_med.id
                rec.description_motif = valid_first_med.description_motif
                rec.date_debut_abscence = valid_first_med.date_debut_abscence
            elif not valid_first_med:
                rec.numero = '1'
                rec.first_med = False
            else:
                rec.numero = rec.numero
                rec.first_med = rec.first_med

    @api.onchange('motif_id')
    def onchange_motif_id(self):
        for rc in self:
            if rc.motif_id:
                rc.description_motif = rc.motif_id.description
            else:
                rc.description_motif = ''

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

    def action_validate(self):  # TODO check for doublon
        self.name = self.env['ir.sequence'].get('hr.demeure') or '/'
        self.state = 'done'
        if self.numero == '1':
            num = '1ere mise en demeure'
        else:
            num = u'2ème mise en demeure'
        self.env['hr.employee.historique'].create({
            'employe_id': self.employe_id.id,
            'document': num,
            'numero': self.name,
            'date_doc': self.s_date,
            # 'date_prise_effet' : self.date_fin,
            'user_id': self.user_id.id,
            'note': 'Motif -> ' + self.motif_id.name,
            'model_name': 'hr.demeure',
            'model_id': self.id,
            'num_embauche': self.employe_id.num_embauche,
        })

    def action_cancel(self):
        self.state = 'cancel'

    def action_archive(self):
        for rec in self:
            rec.state = 'archived'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = 'DRAFT'

        vals['job_id'] = self.env['hr.employee'].browse(vals.get('employe_id')).job_id.id

        return super(models.Model, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_(
                    'Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
            return super(MiseEnDemeure, self).unlink()

    def action_print(self):
        if self.numero == '1':
            return self.env.ref('r_mise_en_demeure.act_report_mise_en_demeure_first').report_action(self)
        else:
            return self.env.ref('r_mise_en_demeure.act_report_mise_en_demeure_second').report_action(self)

    def action_print_ar(self):
        return self.env.ref('r_mise_en_demeure.act_report_mise_en_demeure_first_ar').report_action(self)

    def _check_2_mise(self):
        valid_first_med = self.env['hr.demeure'].search([
            ('state', '=', 'done'),
            ('numero', '=', 1),
            ('date_debut_abscence', '<=', fields.Date.to_string(date.today() + relativedelta(days=1)))])
        for rec in valid_first_med:
            valid_second_med = self.env['hr.demeure'].search(
                [('employe_id', '=', rec.employe_id.id), ('state', '=', 'done'), ('numero', '=', 2)])
            grp = self.env['res.groups'].search([('name', '=', 'Group HR Menu'), ])
            if not valid_second_med:
                for user in grp[0].users:
                    rec.note = 'Veuillez créer la 2eme MED'
                    self.env['mail.activity'].create({
                        'res_id': rec.id,
                        'user_id': user.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'hr.demeure')])[0].id,
                        'res_model': 'r_mise_en_demeure.model_hr_demeure',
                        'res_name': rec.name,
                        'activity_type_id': 4,
                        'note': 'Veuillez créer la 2eme MED',
                        'date_deadline': date.today(),
                    })
