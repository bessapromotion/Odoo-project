# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from datetime import date


class Demeure(models.Model):
    _inherit = 'hr.demeure'

    notif_frt = fields.Boolean(default=False)

    def _check_frt(self):
        valid_second_med = self.env['hr.demeure'].search([('state', '=', 'done'), ('numero', '=', 2), (
            's_date', '<=', fields.Date.to_string(date.today() + relativedelta(days=2)))])
        grp = self.env['res.groups'].search([('name', '=', 'Group HR Menu'), ])
        for rec in valid_second_med:
            frt = self.env['hr.frt'].search([('state', '=', 'valid'), ('notif_frt', '=', False), ('employe_id', '=', rec.employe_id.id)])
            if not frt:
                for user in grp[0].users:
                    self.env['mail.activity'].create({
                        'res_id': rec.id,
                        'user_id': user.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', 'hr.demeure')])[0].id,
                        'res_model': 'r_mise_en_demeure.model_hr_demeure',
                        'res_name': rec.name,
                        'activity_type_id': 4,
                        'note': 'Veuillez créer la décision de fin fonction',
                        'date_deadline': date.today(),
                    })
                    rec.note = 'Veuillez créer la FRT'
                    rec.notif_frt = True
