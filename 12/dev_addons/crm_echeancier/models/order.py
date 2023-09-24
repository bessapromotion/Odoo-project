# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    @api.one
    @api.depends('echeancier_ids')
    def _nbr_echeances(self):
        for rec in self:
            tot_paiement = 0.0
            nbr_ech = 0
            for ech in rec.echeancier_ids:
                if ech.state != 'cancel':
                    tot_paiement += ech.montant
                    nbr_ech += 1

            rec.nbr_echeances = nbr_ech
            rec.total_paiement = tot_paiement
            rec.residual = rec.amount_untaxed - tot_paiement

    @api.depends('total_paiement', 'amount_untaxed', 'echeancier_ids')
    def _affiche_facture(self):
        for rec in self:
            if rec.total_paiement >= rec.amount_untaxed:
                rec.affiche_facture = True
            else:
                rec.affiche_facture = False

    echeancier_ids = fields.One2many('crm.echeancier', 'order_id', string='Echeancier', readonly=True,
                                     domain=[('state', '!=', 'cancel')])
    nbr_echeances = fields.Integer(compute=_nbr_echeances, string='Nombre echeances')
    nbr_echeances_bt = fields.Integer(related='nbr_echeances', string='Echéances')
    total_paiement = fields.Monetary(compute=_nbr_echeances, string='Total paiement echeances')
    total_paiement2 = fields.Monetary()
    affiche_facture = fields.Boolean(compute=_affiche_facture, store=True)
    amount_untaxed2 = fields.Monetary()
    residual = fields.Monetary(compute=_nbr_echeances, string=u'Reste à payer')

    @api.multi
    def action_print_ordre_paiement(self):
        data_obj = self.env['ir.model.data']

        form_data_id = data_obj._get_id('crm_echeancier', 'print_ordre_paiement_wizard_form_view')
        form_view_id = False
        if form_data_id:
            form_view_id = data_obj.browse(form_data_id).res_id

        return {
            'name': 'Assistant impression Ordre de paiement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(form_view_id, 'form'), ],
            'res_model': 'print.ordre.paiement.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_order_id': self.id, 'default_commercial_id': self.user_id.id,
                        'default_mode_paiement_id': self.mode_paiement_id.id},
            'target': 'new',
        }

    @api.multi
    def action_cancel(self):
        state = []
        for rec in self.reservation_ids:
            state.append(rec.state)
        if 'valid' in state:
            raise UserError(_(
                "Vous avez une reservation validée veuillez passer par la procedure d'annualtions et de remboursements."))
        else:
            super(SaleOrder, self).action_cancel()
     
    
    