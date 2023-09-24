# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import conversion

class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    @api.one
    @api.depends('amount_total_signed', 'residual_signed')
    def _calcul_versement_et_racio(self):
        for rec in self:
            rec.total_versement = rec.amount_total_signed - rec.residual_signed
            if rec.amount_total_signed != 0 :
                rec.ratio = rec.total_versement / rec.amount_total_signed * 100
            else:
                rec.ratio = 0

    @api.one
    @api.depends('amount_total_signed', 'taux_objectif')
    def _calcul_total_objectif(self):
        for rec in self:
            rec.objectif = rec.amount_total_signed * rec.taux_objectif

    @api.one
    @api.depends('declare', 'residual_signed')
    def _calcul_declare(self):
        for rec in self:
            rec.tva_declare = rec.declare / 1.09 * 0.09
            rec.notaire = rec.declare * 0.0219 + 27000
            rec.total_declare = rec.tva_declare + rec.notaire + rec.residual_signed
            rec.objectif_declare = (rec.tva_declare + rec.residual_signed) / 3

    @api.one
    @api.depends('date_due')
    def _calcul_period(self):
        for rec in self:
            t = ''
            if rec.date_due:
                if 1 <= rec.date_due.month <= 3:
                    t = 'T1'
                if 4 <= rec.date_due.month <= 6:
                    t = 'T2'
                if 7 < rec.date_due.month < 9:
                    t = 'T3'
                if 10 < rec.date_due.month < 12:
                    t = 'T4'

                rec.period = t
            else:
                rec.period = ''

    @api.one
    @api.depends('invoice_line_ids')
    def _display_Number_To_Word(self):
        for rec in self:
            rec.montant_lettre = conversion.conversion(rec.total_declare)

    total_versement  = fields.Monetary(string='Total Versement', store=True,  compute='_calcul_versement_et_racio')
    # project_id        = fields.Many2one('project.project', string='Projet')
    taux_objectif    = fields.Float(string='Taux Objectif (%)')
    objectif         = fields.Monetary(string='Objectif', store=True,  compute='_calcul_total_objectif')
    ratio            = fields.Float(string='Ratio (%)', store=True, compute='_calcul_versement_et_racio')
    period           = fields.Char(string=u'Période', store=True, compute='_calcul_period')
    mode_achat       = fields.Selection([('1', 'CREDIT'), ('2', 'AUTO'), ], string='Mode Achat', default='2')
    numero           = fields.Integer(string= u'N°')
    declare          = fields.Monetary(string=u'Déclaré' )
    tva_declare      = fields.Monetary(string='TVA', store=True,  compute='_calcul_declare')
    notaire          = fields.Monetary(string='Notaire', store=True,  compute='_calcul_declare')
    total_declare    = fields.Monetary(string='Total', store=True,  compute='_calcul_declare')
    objectif_declare = fields.Monetary(string=u'Objectif Déclaré', store=True,  compute='_calcul_declare')
    charge_recouv_id = fields.Many2one('res.users', string='Chargé de Recouvrement')  # , required=1)
    montant_lettre = fields.Char(compute='_display_Number_To_Word', string='Montant lettre', readonly=1)

    @api.multi
    def compute_new_fields(self):
        self.objectif = self.amount_total_signed * self.taux_objectif
        self.total_versement = self.amount_total_signed - self.residual_signed
        if self.amount_total_signed != 0:
            self.ratio = self.total_versement / self.amount_total_signed * 100
        else:
            self.ratio = 0

        t = ''
        if self.date_due:
            if 1 <= self.date_due.month <= 3:
                t = 'T1'
            if 4 <= self.date_due.month <= 6:
                t = 'T2'
            if 7 < self.date_due.month < 9:
                t = 'T3'
            if 10 < self.date_due.month < 12:
                t = 'T4'

            self.period = t
        else:
            self.period = ''

        self.tva_declare = self.declare / 1.09 * 0.09
        self.notaire = self.declare * 0.0219 + 27000
        self.total_declare = self.tva_declare + self.notaire + self.residual_signed
        self.objectif_declare = (self.tva_declare + self.residual_signed) / 3
