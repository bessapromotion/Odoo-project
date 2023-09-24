# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import UserError


class Contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    def copy(self, default=None):
        raise UserError(_(
            'La fonction duplication a été désactivée !'))
