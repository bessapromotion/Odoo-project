# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class CrmEcheancier(models.Model):
    _inherit = 'crm.echeancier'

    def get_motif_paiement(self):
        for rec in self:
            rec.motif_paiement = ''
            date_ech_1 = ''
            if rec.type == 'notaire':
                rec.motif_paiement = 'notaire'
            if rec.type == 'tva':
                rec.motif_paiement = 'recouvrement'
            if rec.type == 'tranche' and rec:
                for o in rec.order_id.echeancier_ids:
                    date_ech_1 = o[0].date_paiement
                if rec.date_paiement and date_ech_1 and (date_ech_1 + relativedelta(days=45)):
                    if rec.date_paiement > (date_ech_1 + relativedelta(days=45)):
                        rec.motif_paiement = 'recouvrement'
                    else:
                        rec.motif_paiement = 'vente'

    motif_paiement = fields.Selection(
        [('vente', 'Vente'), ('recouvrement', 'Recouvrement'), ('notaire', 'Notaire')],
        string='MOTIF DE PAIEMENT', compute='get_motif_paiement', store=True)