from odoo import models, fields, api


class ProductChangeQuantity(models.TransientModel):
    _name = "stock.change.product.qty"
    _inherit = 'stock.change.product.qty'

    @api.model
    def default_get(self, fields):
        if 'location_id' in fields: fields.remove('location_id')
        res = super(ProductChangeQuantity, self).default_get(fields)
        return res


class StockPickingType(models.Model):
    _name    = 'stock.picking.type'
    _inherit = 'stock.picking.type'

    mise_a_dispo  = fields.Selection([('no', 'Non interne'),
                                      ('mad', 'Mise a disposition'),
                                      ('rev', 'Reversement')],
                                     string=u'Opération interne', default='no')


class StockPicking(models.Model):
    _name    = 'stock.picking'
    _inherit = 'stock.picking'

    demande_id    = fields.Many2one('demande.achat', string='Demande d\'achat', readonly=1)
    employe_id    = fields.Many2one(related='demande_id.employe_id', string='Demandeur', readonly=1)
    department_id = fields.Many2one(related='demande_id.department_id', string='Department', readonly=1)
    job_id        = fields.Many2one(related='demande_id.employe_id.job_id', string='Fonction', readonly=1)
    project_id    = fields.Many2one('project.project', string='Projet')
    mise_a_dispo  = fields.Selection(related='picking_type_id.mise_a_dispo', string='Opération interne', readonly=1)
