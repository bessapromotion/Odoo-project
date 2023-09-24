# -*- coding: utf-8 -*-
from odoo import models, _,fields 
from odoo.exceptions import UserError


class CreerPaiementWizard(models.TransientModel):
    _inherit = 'creer.paiement.wizard'
    _name = 'creer.paiement.wizard'

    payment_date = fields.Date('Date', required=True, copy=False, default = lambda self: fields.Date.today())