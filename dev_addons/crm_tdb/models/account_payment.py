# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('echeance_id', 'cheque_type', 'mode_paiement_id', 'dl_date')
    def get_motif_paiement(self):
        for rec in self:
            rec.motif_paiement = ''
            date_ech = ''
            if rec.echeance_id:
                if rec.echeance_id.type == 'notaire':
                    rec.motif_paiement = 'notaire'
                if rec.echeance_id.type == 'tva':
                    rec.motif_paiement = 'recouvrement'
                if rec.echeance_id.type == 'tranche' and rec.echeance_id.type_bien != 'cellier':
                    date_ech_1 = self.env['crm.echeancier'].search(
                        [('order_id', '=', rec.echeance_id.order_id.id), ('name', '=', '#1'), ])
                    if len(date_ech_1) > 0:
                        for date in date_ech_1[0].payment_ids:
                            date_ech = date[0].dl_date
                        if rec.dl_date and date_ech:
                            if rec.dl_date > (date_ech + relativedelta(days=45)):
                                rec.motif_paiement = 'recouvrement'
                            else:
                                rec.motif_paiement = 'vente'
                    date_ech_1 = self.env['crm.echeancier'].search(
                        [('order_id', '=', rec.echeance_id.order_id.id), ('name', '=', '#Basculement'), ])
                    if len(date_ech_1) > 0:
                        for date in date_ech_1[0].payment_ids:
                            date_ech = date[0].dl_date
                        if rec.dl_date and date_ech:
                            if rec.dl_date > (date_ech + relativedelta(days=45)):
                                rec.motif_paiement = 'recouvrement'
                            else:
                                rec.motif_paiement = 'vente'
                if rec.echeance_id.type == 'tranche' and rec.echeance_id.type_bien == 'Cellier':
                    rec.motif_paiement = 'cellier'
                if rec.mode_paiement_id.name == 'Cheque' and rec.cheque_type == 'credit':
                    rec.motif_paiement = 'credit'

    motif_paiement = fields.Selection(
        [('vente', 'Vente'), ('recouvrement', 'Recouvrement'), ('notaire', 'Notaire'), ('cellier', 'Cellier'),
         ('credit', 'Crédit')],
        string='MOTIF DE PAIEMENT', compute='get_motif_paiement', store=True)
