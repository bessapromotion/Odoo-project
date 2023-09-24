from odoo import api, fields, models


class Bill(models.Model):
    _name = "bill"
    _description = "Coins/Bills"

    name = fields.Char("Name")
    value = fields.Float("Coin/Bill Value", required=True, digits='Product Price')

    @api.model
    def name_create(self, name):
        result = super().create({"name": name, "value": float(name)})
        return result.name_get()[0]
