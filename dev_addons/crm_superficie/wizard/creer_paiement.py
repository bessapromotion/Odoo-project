# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class CreerPaiementOutWizard(models.TransientModel):
    _inherit = 'creer.paiement.out.wizard'

    # @api.multi
    def action_appliquer(self):
        super(CreerPaiementOutWizard, self).action_appliquer()
        if self.name.state == 'done':
            echeances = self.env['crm.echeancier'].search([('remboursement_id', '=',self.name.id)])
            if echeances.exists():
                echeances[0].state = 'done'
