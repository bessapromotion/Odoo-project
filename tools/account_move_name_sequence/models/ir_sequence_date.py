from odoo import fields, models


class IrSequenceDate(models.Model):
    _name = "ir.sequence.date"

    date_to = fields.Date('Date Fin')

    def action_validate(self):
        print("ok")