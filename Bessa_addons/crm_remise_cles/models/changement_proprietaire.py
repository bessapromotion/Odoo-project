# -*- coding: UTF-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import date


class ChangementProprietaire(models.Model):
    _name = 'changement.proprietaire'
    _description = u'Changement Proprietaire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char('Numero', readonly=1)
    reservation_id = fields.Many2one('crm.reservation', string=u'Réservation', required=True,
                                     states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(related='reservation_id.partner_id', string='Propriétaire Actuel', readonly=1,
                                 store=True)
    order_id = fields.Many2one(related='reservation_id.order_id', required=1, readonly=1,
                               string=u'Réference Bon de commande',
                               states={'draft': [('readonly', False)]}, domain="[('state', 'not in', ('cancel', "
                                                                               "'sent', 'draft'))]")
    commercial_id = fields.Many2one(related='reservation_id.commercial_id', string='Commercial', readonly=1, store=True)
    project_id = fields.Many2one(related='reservation_id.project_id', string='Projet', readonly=1,
                                 states={'draft': [('readonly', False)]}, store=True)
    date = fields.Date('Date', required=1, default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', u'Validée'), ('cancel', 'Annulé')], string='Etat', default='draft',
                             tracking=True)
    product_ids = fields.One2many(related='reservation_id.product_ids', string='APPARTEMENT', readonly=1,
                                  states={'draft': [('readonly', False)]})
    product_name = fields.Char(related='product_ids.name.name', string='Nom de l\'Appartement')
    product = fields.Many2one(related='product_ids.name', string='Appartement')
    old_partner_id = fields.Many2one('res.partner', string='Ancien Propriétaire', store=True, readonly=1)
    new_partner_id = fields.Many2one('res.partner', string='Nouveau Propriétaire', store=True)
    # product_ids = fields.One2many(related='reservation_id.product_ids', string='Appartement', readonly=1)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    observation = fields.Char(string="Observation")
    currency_id = fields.Many2one('res.currency', string='Devise', store=True,
                                  default=lambda self: self.env.company.currency_id.id)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('changement.proprietaire') or '/'

        return super(ChangementProprietaire, self).create(vals)

    # @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le dossier est déjà validé !'))
        else:
            # self.product_ids.unlink()

            rec = super(ChangementProprietaire, self).unlink()
            return rec

    def action_validate(self):
        if self.new_partner_id:
            # sale_order
            self.old_partner_id = self.partner_id
            self.order_id.partner_id = self.new_partner_id
            self.order_id.changement_proprietaire = True
            # crm_reservation
            self.reservation_id.partner_id = self.new_partner_id
            # product_template
            self.product.client_id = self.new_partner_id
            payments = self.env['account.payment'].search([('partner_id', '=', self.old_partner_id.id)])
            # print(payments)
            for p in payments:
                # print(p.partner_id)
                p.partner_id = self.new_partner_id.id
                # print(p.partner_id)
            moves = self.env['account.move'].search([('partner_id', '=', self.old_partner_id.id)])
            # print(moves)
            for m in moves:
                print(m.partner_id)
                m.partner_id = self.new_partner_id.id
            moves_line = self.env['account.move.line'].search([('partner_id', '=', self.old_partner_id.id)])
            # print(moves_line)
            for l in moves_line:
                # print(l.partner_id)
                l.partner_id = self.new_partner_id.id
            self.state = 'valid'

    def action_cancel(self):
        self.state = 'cancel'
