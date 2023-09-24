# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.tools import conversion
from odoo.exceptions import UserError


class Ems(models.Model):
    _name = 'hr.ems'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'EMS'

    employe_id = fields.Many2one('hr.employee', string='Employé', )
    type = fields.Selection([('frt', 'FRT'),
                             ('contract', 'Contrat'), ], string='Type')
    date_entree = fields.Date(string=u'Date Entrée')
    date_sortie = fields.Date(string=u'Date Sortie')
    company_id = fields.Many2one('res.company', string=u'Société', )
    gender = fields.Selection(related='employe_id.gender', store=True)
    marital = fields.Selection(related='employe_id.marital', store=True)
    ss_num = fields.Char(related='employe_id.ss_num', store=True)
    compte_num = fields.Char(related='employe_id.compte_num', store=True)
    job_id = fields.Many2one(related='employe_id.job_id', store=True)
    birthday = fields.Date(related='employe_id.birthday', store=True, string='Date de naissance')
    place_of_birth = fields.Char(related='employe_id.place_of_birth', store=True, string='Lieu de naissance')
    adresse_simple = fields.Char(related='employe_id.adresse_simple', store=True, string='Adresse')
    num_cnas = fields.Char(related='company_id.num_cnas', store=True, string='Identifiant')
