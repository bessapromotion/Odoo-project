# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmEcheancier(models.Model):
    _inherit = 'crm.echeancier'

    superficie_id = fields.Many2one('crm.superficie', string='Changement superficie', readonly=1)
    remboursement_id = fields.Many2one('crm.remboursement', string='Remboursement', readonly=1)
