from odoo import api
from odoo import fields, models


class CaisseBill(models.Model):
    _name = "caisse.bill"
    _description = " Caisse Coins/Bills"

    bill_id = fields.Many2one('bill', string='Pieces/Billets')
    nombre = fields.Integer("Nombre", required=True, digits=0)
    montant = fields.Monetary(string='Montant', store=True, compute='calcul_montant',
                              tracking=True, digits=(12, 2))
    currency_id = fields.Many2one('res.currency', string='Devise', store=True,
                                  default=lambda self: self.env.company.currency_id.id)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    caisse_id = fields.Many2one('crm.caisse', string='Caisse')
    open_caisse_id = fields.Many2one('open.caisse.wizard', string='Ouverture de Caisse')
    state = fields.Selection(
        [('open', 'Ouverture'), ('close', 'Cloture')], string='Status', default='open', required=True, tracking=True)

    @api.onchange('nombre', 'bill_id')
    def calcul_montant(self):
        for rec in self:

            if rec.bill_id and rec.nombre:
                rec.montant = rec.bill_id.value * rec.nombre
