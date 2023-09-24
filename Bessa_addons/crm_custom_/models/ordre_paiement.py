# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class OrdrePaiement(models.Model):
    _name = 'ordre.paiement'
    _inherit = 'ordre.paiement'

    state = fields.Selection([('open', 'En instance de paiement'), ('done', u'Terminé'), ('cancel', u'Annulé')],
                             tracking=True)

    project_id = fields.Many2one(related='order_id.project_id', string='Projet', store=True)

    # annulation
    motif_annulation_id = fields.Many2one('annuler.paiement.motif', string='Motif d\'annulation', readonly=True,
                                          tracking=True)

    # add default type and charge_ok after installing charge & tag module
    def action_print_recu_paiement(self):
        if self.company_id.id != self.env.company.id:
            raise UserError(_(u'Veuillez sélectionner la société %s', self.company_id.name))
        req1 = "delete from echeance_amount_wizard"
        req2 = "delete from creer_paiement_wizard"
        self._cr.execute(req1, )
        self._cr.execute(req2, )

        view_id = self.env['ir.model.data']._xmlid_to_res_id('crm_echeancier.creer_paiement_wizard_form_view')

        return {
            'name': 'Assistant impression recu de paiement',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(view_id, 'form'), ],
            'res_model': 'creer.paiement.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_name': self.id,
                        'default_amount': self.amount,
                        'default_amount_commercial': self.amount,
                        'default_payment_date': self.date,
                        'default_communication': self.objet,
                        'default_doc_payment_id': self.doc_payment_id.id,
                        'default_mode_paiement_id': self.mode_paiement_id.id,
                        'default_partner_reference': self.partner_reference,
                        'default_observation': self.observation,
                        'default_type': 'versement',
                        'default_charge_ok': False,
                        },
            'target': 'new',
        }
