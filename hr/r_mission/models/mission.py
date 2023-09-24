# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class Mission(models.Model):
    _name = 'hr.mission'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Ordre de mission'

    name = fields.Char(u'Numéro', default='/', readonly=1)
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company,
                                 readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1)

    date = fields.Date(u'Date établissement', default=lambda self: fields.Date.today(), readonly=1,
                       states={'draft': [('readonly', False)]})
    date_depart = fields.Datetime(u'Date de départ', required=True, readonly=1,
                                  states={'draft': [('readonly', False)], 'autorisation': [('readonly', False)],
                                          'planned': [('readonly', False)]})
    date_retour = fields.Datetime('Date de retour',
                                  states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    destination = fields.Char(u'Se rendre à', readonly=1, states={'draft': [('readonly', False)]})
    motif = fields.Char(u'Motif de départ', required=True, readonly=1,
                        states={'draft': [('readonly', False)], 'autorisation': [('readonly', False)],
                                'planned': [('readonly', False)]})
    moyen_id = fields.Many2one('hr.mission.moyen', string='Moyen de transport', required=True, readonly=1,
                               states={'draft': [('readonly', False)], 'autorisation': [('readonly', False)]})
    type_moyen = fields.Selection(related='moyen_id.type', string='Type moyen de transport', readonly=1)
    avec_chauffeur = fields.Boolean('Avec chauffeur', readonly=1,
                                    states={'draft': [('readonly', False)], 'autorisation': [('readonly', False)]})
    prestataire_id = fields.Many2one('res.partner', string='Prestataire', readonly=1,
                                     states={'draft': [('readonly', False)], 'planned': [('readonly', False)]})
    chauffeur_id = fields.Many2one('hr.employee', string='Chauffeur', readonly=1,
                                   states={'draft': [('readonly', False)], 'autorisation': [('readonly', False)]},
                                   check_company=False)
    observation = fields.Text('Observation')
    chef_mission_id = fields.Many2one('hr.employee', string='Chef de mission', readonly=1,
                                      states={'draft': [('readonly', False)], }, check_company=False)

    employee_ids = fields.One2many('hr.mission.employee', 'mission_id', string='Missionnaires', readonly=1,
                                   states={'draft': [('readonly', False)], 'autorisation': [('readonly', False)]})
    state = fields.Selection([('draft', 'Nouveau'),
                              ('autorisation', u'Autorisation'),
                              ('planned', u'Planifié'),
                              ('open', 'En cours'),
                              ('done', u'Terminé'),
                              ('cancel', u'Annulé')], string='Etat', default='draft')

    def action_planned(self):
        if self.employee_ids:
            num = self.env['ir.sequence'].get('hr.mission') or '/'
            self.name = num + '/' + self.company_id.name + '/' + str(date.today())[:4]
            self.state = 'planned'
            for rec in self.employee_ids:
                self.env['hr.employee.historique'].create({
                    'employe_id': rec.name.id,
                    'document': 'Ordre de mission ',
                    'numero': self.name,
                    'date_doc': self.date,
                    'user_id': self.user_id.id,
                    'note': 'Objet -> ' + self.motif,
                    'model_name': 'hr.mission.employee',
                    'model_id': rec.id,
                    'num_embauche': rec.name.num_embauche,
                })
            else:
                raise UserError(
                    _('Veuillez sélectionner les missionnaires'))

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(
                'Ce document est validé, vous n\'avez pas l\'autorisation de le supprimer.\nVeuillez contacter l\'administrateur'))
        return super(models.Model, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = 'DRH/DRAFT'

        return super(models.Model, self).create(vals)

    def action_print(self):
        return self.env.ref('r_mission.act_report_ordre_mission').report_action(self)


class MissionMoyen(models.Model):
    _name = 'hr.mission.moyen'
    _description = 'Moyen de transport'

    name = fields.Char('Moyen')
    type = fields.Selection([('Interne', 'Interne'), ('Prestataire', 'Prestataire'), ('Autre', 'Autre')], string='Type',
                            required=True)
