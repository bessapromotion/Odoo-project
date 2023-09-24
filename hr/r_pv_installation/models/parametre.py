# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


class Contract(models.Model):
    _inherit = 'res.company'

    pv_soussigné_par = fields.Char('PV soussigné par')
