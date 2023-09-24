from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    # @api.depends('amount_total', 'echeancier_ids', 'num_dossier', 'total_paiement')
    # def compute_mt_encaisse(self):
    #     for rec in self:
    #         rec.mt_encaisse = 0
    #         # rec.prix_vente_devis = 0
    #         rec.taux = 0
    #         if rec.nbr_echeances > 0 and rec.order_line:
    #             rec.mt_encaisse = rec.echeancier_ids[0].montant
    #             # rec.prix_vente_devis = rec.order_line[0].price_unit
    #         if rec.amount_total != 0:
    #             rec.taux = (rec.mt_encaisse / rec.amount_total) * 100

    @api.depends('amount_total', 'echeancier_ids', 'num_dossier', 'total_paiement')
    def compute_mt_encaisse(self):
        delai = self.env['ir.config_parameter'].sudo().get_param('encaissement_recouvrement', 'value')
        for rec in self:
            rec.mt_encaisse = 0
            date_ech = ''
            rec.taux = 0
            if delai and rec.nbr_echeances > 0:
                date_ech_1 = self.env['crm.echeancier'].search(
                    [('order_id', '=', rec.id), ('name', '=', '#1'), ])
                if len(date_ech_1) > 0:
                    for date in date_ech_1[0].payment_ids:
                        date_ech = date[0].dl_date
                    if date_ech and len(rec.echeancier_ids) > 0:
                        for ech in rec.echeancier_ids:
                            if len(ech.payment_ids) > 0:
                                for p in ech.payment_ids:
                                    if p.dl_date and ech.type != 'notaire' and date_ech and p.state != 'cancel':
                                        if p.dl_date < (date_ech + relativedelta(days=45)):
                                            rec.mt_encaisse = rec.mt_encaisse + p.amount

            if rec.amount_total != 0:
                rec.taux = (rec.mt_encaisse / rec.amount_total) * 100

    @api.depends('echeancier_ids', 'objectif', 'num_dossier')
    def compute_mt_encaisse_recouvrement(self):
        delai = self.env['ir.config_parameter'].sudo().get_param('encaissement_recouvrement', 'value')
        for rec in self:
            rec.mt_recouvrement = 0
            date_ech = ''
            rec.taux_2 = 0
            if delai and rec.nbr_echeances > 0:
                date_ech_1 = self.env['crm.echeancier'].search(
                    [('order_id', '=', rec.id), ('name', '=', '#1'), ])
                if len(date_ech_1) > 0:
                    for date in date_ech_1[0].payment_ids:
                        date_ech = date[0].dl_date
                    if date_ech and len(rec.echeancier_ids) > 0:
                        for ech in rec.echeancier_ids:
                            if len(ech.payment_ids) > 0:
                                for p in ech.payment_ids:
                                    if p.dl_date and ech.type != 'notaire' and date_ech and ech.name != '#Basculement' and p.state != 'cancel':
                                        if p.dl_date > (date_ech + relativedelta(days=45)):
                                            rec.mt_recouvrement = rec.mt_recouvrement + p.amount
                date_ech_1 = self.env['crm.echeancier'].search(
                    [('order_id', '=', rec.id), ('name', '=', '#Basculement'), ])
                if len(date_ech_1) > 0:
                    for date in date_ech_1[0].payment_ids:
                        date_ech = date[0].dl_date
                    if date_ech and len(rec.echeancier_ids) > 0:
                        for ech in rec.echeancier_ids:
                            if len(ech.payment_ids) > 0:
                                for p in ech.payment_ids:
                                    if p.dl_date and ech.type != 'notaire' and date_ech and p.state != 'cancel':
                                        if p.dl_date > (date_ech + relativedelta(days=45)):
                                            rec.mt_recouvrement = rec.mt_recouvrement + p.amount
                if rec.objectif != 0:
                    rec.taux_2 = rec.mt_recouvrement / rec.objectif

    @api.depends('echeancier_ids', 'num_dossier')
    def get_valeur_ttc(self):
        for rec in self:
            rec.valeur_ttc = 0
            rec.mt_paye = 0
            if rec.nbr_echeances > 0:
                for ech in rec.echeancier_ids:
                    if ech.type != 'notaire':
                        rec.valeur_ttc = rec.valeur_ttc + ech.montant_prevu
                        rec.mt_paye = rec.mt_paye + ech.montant
                    if ech.type == 'tva':
                        rec.valeur_ttc2 = rec.amount_total + ech.montant_prevu
                        rec.total_tva = ech.montant_prevu
                        rec.tva_paye = ech.montant
                rec.mt_reste = rec.valeur_ttc - rec.mt_paye

    @api.depends('validity_date', 'charge_recouv_id', 'obj')
    def get_objectif(self):
        for rec in self:
            rec.objectif = 0
            if rec.charge_recouv_id and rec.validity_date:
                year = rec.validity_date.strftime('%Y')
                month = rec.validity_date.strftime('%m')
                obj = self.env['res.users.objectif'].search(
                    [('month', '=', month), ('year', '=', year), ('user_id', '=', rec.charge_recouv_id.id)])
                if obj:
                    rec.objectif = obj[0].objectif

    obj = fields.One2many(related='charge_recouv_id.objectif_ids')

    mt_encaisse = fields.Float(compute='compute_mt_encaisse', string='M. encaissé à la vente', store=True)
    mt_recouvrement = fields.Float(compute='compute_mt_encaisse_recouvrement', string='M. recouvrement', store=True)
    taux = fields.Float(compute='compute_mt_encaisse', string='Taux Encaissement%', store=True, group_operator='avg')
    taux_2 = fields.Float(compute='compute_mt_encaisse_recouvrement', string='Taux Recouverment%', store=True,
                          group_operator='sum')
    objectif = fields.Monetary(string='Objectif Commercial', compute='get_objectif', store=True)
    valeur_ttc = fields.Monetary(string='Valeur du bien TTC', store=True, compute='get_valeur_ttc')
    valeur_ttc2 = fields.Monetary(string='Total TTC', store=True, compute='get_valeur_ttc')
    mt_paye = fields.Monetary(string='M. Payé', store=True, compute='get_valeur_ttc')
    mt_reste = fields.Monetary(string='M. Rest à payé', store=True, compute='get_valeur_ttc')
    total_tva = fields.Monetary(string='Total TVA', store=True, compute='get_valeur_ttc')
    tva_paye = fields.Monetary(string='TVA Payé', store=True, compute='get_valeur_ttc')


class CrmReservation(models.Model):
    _name = 'crm.reservation'
    _inherit = 'crm.reservation'

    mt_encaisse = fields.Float(related='order_id.mt_encaisse', string='M. encaissé à la vente', store=True)
