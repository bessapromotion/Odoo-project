# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    project_id  = fields.Many2one('project.project', string='Projet')
    mode_achat = fields.Selection(related='partner_id.mode_achat', string='Mode Achat', readonly=True)
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement', help='a titre d\'information, puisque le mode est ressaisi lors du paiement')
    charge_recouv_id = fields.Many2one('res.users', string='Chargé de Recouvrement')
    # charge_recouv_id = fields.Many2one('res.users', required=1, string='Chargé de Recouvrement', states={'draft': [('required', False)]})
    num_dossier = fields.Char('N° Dossier')
