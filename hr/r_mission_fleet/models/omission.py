# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class Mission(models.Model):
    _inherit = 'hr.mission'

    @api.depends('employee_ids')
    def _autorise_pour(self):
        for rec in self:
            if rec.employee_ids:
                rec.autorise_pour = rec.employee_ids[0].name.name
            else:
                rec.autorise_pour = ''

    use_fleet = fields.Boolean(related='moyen_id.use_fleet')
    autorisation = fields.Boolean(related='moyen_id.autorisation')
    vehicule_id = fields.Many2one('fleet.vehicle', string=u'Véhicule', readonly=1, states={'draft': [('readonly', False)], 'autorisation': [('readonly', False)]})
    km_depart = fields.Float(u'Kilométrage départ', readonly=1)
    km_arrivee = fields.Float(u'Kilométrage arrivée', readonly=1)
    motif_refus = fields.Text('Motif de refus', readonly=1)
    message = fields.Char(default='Cette mission doit etre autorisée pour l\'utilisation du véhicule', readonly=1)
    autorise_par_id = fields.Many2one('res.users', string=u'Décision par', readonly=True)
    autorise_date   = fields.Datetime('Autorisé le', readonly=True)
    autorise_pour   = fields.Char(compute=_autorise_pour, string='Autorisation pour')
    date_depart_prevue = fields.Datetime(u'Date de départ prévue', required=True, readonly=1, states={'draft': [('readonly', False)]})
    date_depart = fields.Datetime(u'Date de départ', readonly=1, required=False)
    date_retour_prevue = fields.Datetime(u'Date de retour prévue', readonly=1, states={'draft': [('readonly', False)]})
    date_retour = fields.Datetime('Date de retour', readonly=1)

    @api.onchange('vehicule_id')
    def onchange_vehicle(self):
        if self.vehicule_id:
            self.km_depart = self.vehicule_id.odometer
        else:
            self.km_depart = 0.0

    def action_planned(self):
        if self.employee_ids:
            self.name = self.env['ir.sequence'].get('hr.mission') or '/'
            if self.autorisation:
                self.state = 'autorisation'
            else:
                self.state = 'planned'
                for rec in self.employee_ids:
                    self.env['hr.employee.historique'].create({
                        'employe_id': rec.name.id,
                        'document': 'Ordre de mission ',
                        'numero': self.name,
                        'date_doc': self.date,
                        # 'date_prise_effet' : self.date_effet,
                        'user_id': self.user_id.id,
                        'note': 'Objet -> ' + self.motif,
                        'model_name': 'hr.mission.employee',
                        'model_id': rec.id,
                        'num_embauche': rec.name.num_embauche,
                    })
        else:
            raise UserError(
                _('Veuillez sélectionner les missionnaires'))

    def action_autoriser_ok(self):
        return {
            'name': _('Autorisation'),
            'view_mode': 'form',
            'res_model': 'hr.mission.autorisation.wizard',
            'view_id': self.env.ref('r_mission_fleet.hr_mission_autorisation_wizard_form_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_mission_id'    : self.id,
                'default_auto'          : True,
                'default_vehicule_id'   : self.vehicule_id.id,
                'default_avec_chauffeur': self.avec_chauffeur,
                'default_chauffeur_id'  : self.chauffeur_id.id,
                'default_employee'  : self.autorise_pour,
            },
            'target': 'new',
        }

    def action_autoriser_nok(self):
        return {
            'name': _('Autorisation'),
            'view_mode': 'form',
            'res_model': 'hr.mission.autorisation.wizard',
            'view_id': self.env.ref('r_mission_fleet.hr_mission_autorisation_wizard_form_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_mission_id'    : self.id,
                'default_auto'          : False,
                'default_vehicule_id'   : self.vehicule_id.id,
                'default_avec_chauffeur': self.avec_chauffeur,
                'default_chauffeur_id'  : self.chauffeur_id.id,
            },
            'target': 'new',
        }

    def action_print_autorisation(self):
        return self.env.ref('r_mission_fleet.act_report_autorisation').report_action(self)

    def action_start(self):
        if not self.vehicule_id and self.use_fleet:
            raise UserError(_("Veuillez sélectionner le véhicule prévu cette mission"))

        return {
            'name': _('Marquer le départ'),
            'view_mode': 'form',
            'res_model': 'hr.mission.depart.wizard',
            'view_id': self.env.ref('r_mission_fleet.hr_mission_depart_wizard_form_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_mission_id': self.id,
                'default_date_depart': self.date_depart_prevue,
                'default_km_depart': self.vehicule_id.odometer,
            },
            'target': 'new',
        }

    def action_done(self):
        return {
            'name': _('Marquer l\'arrivée'),
            'view_mode': 'form',
            'res_model': 'hr.mission.arrivee.wizard',
            'view_id': self.env.ref('r_mission_fleet.hr_mission_arrivee_wizard_form_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_mission_id': self.id,
                'default_date_arrivee': self.date_retour_prevue,
            },
            'target': 'new',
        }


class MissionMoyen(models.Model):
    _inherit = 'hr.mission.moyen'

    use_fleet = fields.Boolean('Utiliser parc auto')
    autorisation = fields.Boolean('Autorisation')
