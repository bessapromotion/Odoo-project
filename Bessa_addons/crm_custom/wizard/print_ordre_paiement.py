# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.tools import conversion
from odoo.exceptions import UserError


class PrintOrdrePaiementWizard(models.TransientModel):
    _inherit = 'print.ordre.paiement.wizard'


    date                 = fields.Date('Date du paiement', required=True, default=lambda self: fields.Date.today())
