# -*- coding: utf-8 -*-
from odoo import models, fields


class BessaCrmSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'bessa.crm.config.settings'

    default_mtn_min_reserv = fields.Float(default_model='crm.reservation', string='Montant minimum', help="""Le client doit valider au moins ce montant avant de pouvoir valider la réservation""")
    default_mtn_min_print  = fields.Float(default_model='crm.reservation', string='Pourcentage minimum', help=""" """)
