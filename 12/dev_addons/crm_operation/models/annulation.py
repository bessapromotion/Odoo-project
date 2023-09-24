# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class TypeAnnulation(models.Model):
    _name = 'crm.annulation.type'
    _description = 'Type Annulation'

    name = fields.Char('Type', help='Type Annulation' )


class CrmAnnulation(models.Model):
    _name = 'crm.annulation'
    _description = 'Annulation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    def _get_default_type(self):
        rec = self.env['crm.annulation.type'].search([('name', '=', 'Annulation')])
        if rec.exists():
            return rec.id
        else:
            return None

    name           = fields.Char('Numero', readonly=1)
    commercial_id = fields.Many2one('res.users', required=1, string='Commercial', readonly=1,
                                    states={'draft': [('readonly', False)]})
    date      = fields.Date('Date', required=1, default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    type_id   = fields.Many2one('crm.annulation.type', string='Type', default=_get_default_type, readonly=1, states={'draft': [('readonly', False)]})
    motif     = fields.Text('Motif', readonly=1, states={'draft': [('readonly', False)]})
    state     = fields.Selection([('draft', 'Nouveau'),
                              ('valid', 'Validée'),
                              ('cancel', 'Annulée'), ], string='Etat', default='draft', track_visibility='onchange')

    source = fields.Char('Source', readonly=1)
    reservation_id = fields.Many2one('crm.reservation', string='Réservation', required=True, readonly=1, states={'draft': [('readonly', False)]})
    partner_id    = fields.Many2one(related='reservation_id.partner_id', string='Client', readonly=1, store=True)
    phone         = fields.Char(related='partner_id.phone', string='Téléphone', readonly=1)
    mobile        = fields.Char(related='partner_id.mobile', string='Mobile', readonly=1)
    photo         = fields.Binary(related='partner_id.image', string='Photo')
    product_ids   = fields.One2many(related='reservation_id.product_ids', string='Appartement', readonly=1)
    project_id     = fields.Many2one(related='reservation_id.project_id', string='Projet', readonly=1, store=True)
    date_reservation = fields.Date(related='reservation_id.date', string=u'Date réservation', readonly=1, store=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('crm.annulation') or '/'

        return super(CrmAnnulation, self).create(vals)

    @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Suppression non autorisée ! \n\n  L\'annulation est déjà validée !'))
        else:
            # self.product_ids.unlink()

            rec = super(CrmAnnulation, self).unlink()
            return rec

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_validate(self):
        self.state = 'valid'
        self.partner_id.etat = 'Prospect'
        self.reservation_id.action_cancel()

    @api.onchange('reservation_id')
    def onchange_reservation(self):
        if self.reservation_id:
            self.commercial_id = self.reservation_id.commercial_id.id

    @api.multi
    def action_print(self):
        return self.env.ref('crm_operation.act_report_annulation').with_context({'discard_logo_check': True}).report_action(self)
