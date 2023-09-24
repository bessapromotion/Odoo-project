
from odoo import models, fields


class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _inherit = 'purchase.requisition'

    demande_id = fields.Many2one('demande.achat', string='Demande Achat')
    objet = fields.Char('Objet de la demande')
    picking_type_id = fields.Many2one('stock.picking.type')

