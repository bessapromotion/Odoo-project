# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    echeance_id = fields.Many2one('crm.echeancier', string=u'Echéance', readonly=1,
                                  states={'draft': [('readonly', False)]})
    order_id = fields.Many2one(related='echeance_id.order_id', string='Devis', store=True)
    num_dossier = fields.Char(related='order_id.num_dossier', string='N° Dossier', store=True)
    project_id = fields.Many2one(related='echeance_id.project_id', string='Projet', store=True)
    commercial_id = fields.Many2one(related='order_id.user_id', required=1, string='Commercial', readonly=1, store=True,
                                    tracking=True)
    type_bien = fields.Char(related='order_id.type_bien', required=1, string='Type du bien', readonly=1, store=True,
                            tracking=True)
    ref = fields.Char(related='move_id.ref', store=True, copy=False, index=True, readonly=True)
    state = fields.Selection(related='move_id.state', store=True, related_sudo=False)
    type = fields.Selection([('charge', 'Charge'),
                             ('tag', u'Tag'), ('versement', u'Versement'), ('transfert', 'Transfert de fond')], string='Type du paiement', store=True,
                            tracking=True, default='versement')
    charge_ok = fields.Boolean(string="Charge&tag", default=False, store=True)

    @api.onchange('type')
    def update_charge_ok(self):
        if self.type in ('charge', 'tag'):
            self.charge_ok = True
        else:
            self.charge_ok = False
