# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime

# class MailActivity(models.Model):
#     _name    = 'mail.activity'
#     _inherit = 'mail.activity'
#
#     date_deadline = fields.Datetime('Due Date', index=True, required=True, default=fields.Datetime.now)

class MailMail(models.Model):
    _name = 'mail.mail'
    _inherit = 'mail.mail'

    state = fields.Selection([
        ('outgoing', 'Outgoing'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('exception', 'Delivery Failed'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
    ], 'Status', readonly=True, copy=False, default='outgoing')