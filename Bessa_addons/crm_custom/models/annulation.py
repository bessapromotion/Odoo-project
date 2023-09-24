# -*- coding: utf-8 -*-

from odoo import models, fields


class CrmAnnulation(models.Model):
    _name = 'crm.annulation'
    _inherit = 'crm.annulation'

    name = fields.Char('Numero', readonly=1)
    reservation_id = fields.Many2one('crm.reservation', string='Réservation', required=True, readonly=1,
                                     states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(related='reservation_id.partner_id', string='Client', readonly=1, store=True)
    type_annulation = fields.Selection([('desistement', 'desistement'),
                                        ('annulation', 'Annulation'),
                                        ('changement', 'Changement de propriétaire')], string='Type d\'annulation',
                                       default='desistement')

    def action_validate(self):
        print(self.type_annulation)
        if self.type_annulation == 'annulation':
            self.name = self.env['ir.sequence'].get('crm.annulation') or '/'
        if self.type_annulation == 'desistement':
            self.name = self.env['ir.sequence'].get('crm.desistement') or '/'
        self.state = 'valid'
        if self.partner_id.nbr_produit == 1:
            self.partner_id.etat = 'Client Perdu'
        else:
            if self.partner_id.etat != 'Acquéreur':
                self.partner_id.etat = 'Réservataire'
        self.reservation_id.action_cancel(motif=self.type_annulation)

