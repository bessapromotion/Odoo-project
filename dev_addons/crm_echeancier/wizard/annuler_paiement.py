# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime


class AnnulerPaiementWizard(models.TransientModel):
    _name = 'annuler.paiement.wizard'
    _description = u'Annuler le paiement'

    name = fields.Many2one('ordre.paiement', string='Ordre de paiement', required=1, readonly=1,
                           default=lambda self: self.env.context['active_id'])
    echeance_id = fields.Many2one(related='name.echeance_id', string='Echeance')
    order_id = fields.Many2one(related='name.order_id', string='Commande', readonly=True)
    partner_id = fields.Many2one(related='name.partner_id', string='Client', readonly=True)
    payment_id = fields.Many2one('account.payment', string='Payment', readonly=True, required=True)
    observation = fields.Text('Observation', required=False)
    motif_annulation_id = fields.Many2one('annuler.paiement.motif', string='Motif d\'annulation', required=True)

    def action_appliquer(self):
        self.name.echeance_id.state = 'open'
        self.name.state = 'cancel'
        self.name.motif_annulation_id = self.motif_annulation_id.id
        self.name.annuler_user_id = self.env.user
        self.name.date_annulation = fields.Datetime.now()
        # for rec in self.echeance_id.payment_ids:
        #     if rec.amount == self.name.amount:
        self.payment_id.action_draft()
        self.payment_id.action_cancel()


class AnnulerPaiemenMotif(models.Model):
    _name = 'annuler.paiement.motif'

    name = fields.Char('Motif', required=True)
