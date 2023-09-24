# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = 'account.payment'

    # @api.depends('amount')
    # def _display_number_to_word(self):
    #     for rec in self:
    #         rec.amount_lettre = conversion.conversion(rec.amount)

    old_sequence = fields.Char('old')

    charge_id = fields.Many2one('charge.annual', string=u'Charge/ Tag Référence',
                                domain=" ['&',('partner_id','=',partner_id),('type_doc','=',type)]")
    num_charge = fields.Char(related='charge_id.name', string='Référence')
    num_dossier_charge = fields.Char(related='charge_id.num_dossier', string='N° dossier')
    order_id_charge = fields.Many2one(related='charge_id.order_id', string='Réf du devis')
    project_id_charge = fields.Many2one(related='charge_id.project_id', string='Projet')
    order_paiement_id = fields.Many2one(comodel_name="ordre.paiement.charge", string='Ordre de paiement', readonly=1)
    # type = fields.Selection([('charge', 'Charge'),
    #                          ('tag', u'Tag'), ('versement', u'Versement')], string='Type du paiement', store=True,
    #                         tracking=True, default='versement')
    duree = fields.Integer(u'Nombre d\'années')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    # charge_ok = fields.Boolean(string="Charge&tag", default=False, store=True)
    product_name = fields.Char(related='charge_id.product_name', string=u'Bien')
    year_ids = fields.Many2many('charge.year', string=u'Années',
                                states={'draft': [('readonly', False)]})
    type_paiement = fields.Selection([('year', 'Annuel'),
                                      ('month', u'Mensuel')], string='Paiement',
                                     tracking=True)
    month_ids = fields.Many2many('charge.month', string=u'Mois',
                                 states={'draft': [('readonly', False)]})
    remise = fields.Boolean(u'Paiement Remise des clés',default=False)

