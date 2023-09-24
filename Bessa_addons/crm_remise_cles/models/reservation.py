# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError
from datetime import datetime, date


class CrmReservation(models.Model):
    _name = 'crm.reservation'
    _inherit = 'crm.reservation'

    remise_id = fields.Many2one('remise.cles', string=u'Remise de clés')
    decision_id = fields.Many2one('decision.affectation', string=u'Décision', readonly=1)
