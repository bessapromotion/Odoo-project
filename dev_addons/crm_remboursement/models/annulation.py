# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class CrmDesistement(models.Model):
    _name = 'crm.desistement'
    _description = 'Desistement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char('Numero', readonly=1)
    commercial_id = fields.Many2one('res.users', required=1, string='Commercial', readonly=1,
                                    states={'desistement': [('readonly', False)]})
    charge_rembours_id = fields.Many2one('res.users', required=1,
                                         string=u'Chargé remboursement')  # , readonly=1, states={'desistement': [('readonly', False)]})
    date = fields.Date('Date', required=1, default=date.today())
    motif = fields.Text('Motif')
    # mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement')
    state = fields.Selection([('desistement', u'Désistement déposé'),
                              ('dossier', u'Dossier déposé'),
                              ('annulation', 'Demande d\'annulation'),
                              ('scvalidation', 'Superviseur validation'),
                              ('comptable', u'Controle Comptabilité'),
                              ('done', u'Terminé'),
                              ('cancel', 'Annulée'), ], string='Etat', default='desistement', tracking=True)

    annulation_id = fields.Many2one('crm.annulation', string='Demande Annulation', readonly=True)
    remboursement_id = fields.Many2one('crm.remboursement', string='Remboursement', readonly=True)
    reservation_id = fields.Many2one('crm.reservation', string=u'Réservation', required=1)
    invoice_id = fields.Many2one(related='reservation_id.invoice_id', string='Facture')
    echeancier_ids = fields.One2many(related='reservation_id.echeancier_ids', string='Echeances')
    total_paiement = fields.Monetary(related='reservation_id.total_paiement', string='Montant a rembourser')
    currency_id = fields.Many2one(related='reservation_id.currency_id', string='Devise')

    partner_id = fields.Many2one(related='reservation_id.partner_id', string='Client', readonly=1, store=True)
    phone = fields.Char(related='partner_id.phone', string='Téléphone', readonly=1)
    mobile = fields.Char(related='partner_id.mobile', string='Mobile', readonly=1)
    photo = fields.Binary(related='partner_id.image_1920', string='Photo')
    product_ids = fields.One2many(related='reservation_id.product_ids', string='Appartement', readonly=1)
    project_id = fields.Many2one(related='reservation_id.project_id', string='Projet', readonly=1, store=True)
    date_reservation = fields.Date(related='reservation_id.date', string=u'Date réservation', readonly=1, store=True)
    dossier_ids = fields.One2many('crm.desistement.dossier.line', 'desistement_id', string='Dossiers', readonly=1)
    company_id = fields.Many2one('res.company', u'Société', related='reservation_id.project_id.company_id', store=True)
    type_annulation = fields.Selection([('desistement', 'desistement'),
                                        ('annulation', 'Annulation')], string='Type d\'annulation', required=True,
                                       tracking=True,
                                       default='annulation')

    def create_dossier(self):
        dossier = self.env['crm.desistement.dossier'].search([])
        i = 1
        for rec in dossier:
            doss = self.env['crm.desistement.dossier.line'].search(
                [('dossier_id', '=', rec.id), ('company_id', '=', self.company_id.id),
                 ('desistement_id', '=', self.id)])
            if not doss.exists():
                self.env['crm.desistement.dossier.line'].create({
                    'name': str(i),
                    'dossier_id': rec.id,
                    'recu': False,
                    'desistement_id': self.id,
                    'company_id': self.company_id.id,
                })
                i += 1

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Suppression non autorisée ! \n\n  L\'annulation est déjà validée !'))
        else:
            self.dossier_ids.unlink()

            rec = super(CrmDesistement, self).unlink()
            return rec

    def action_cancel(self):
        self.state = 'cancel'

    @api.onchange('reservation_id')
    def onchange_reservation(self):
        if self.reservation_id:
            self.commercial_id = self.reservation_id.commercial_id.id

    def print_accuse(self):
        return True

    def action_scvalidation(self):
        self.state = 'scvalidation'

    def action_create_annulation(self):
        rec = self.env['crm.annulation.type'].search([('name', '=', 'Annulation')])
        if rec.exists():
            type_id = rec[0].id
        else:
            type_id = self.env['crm.annulation.type'].search([])[0].id

        ann = self.env['crm.annulation'].create({
            'commercial_id': self.commercial_id.id,
            'date': date.today(),
            'type_id': type_id,
            'motif': self.type_annulation,
            'source': self.name,
            'reservation_id': self.reservation_id.id,
            'type_annulation': self.type_annulation,
        })

        self.annulation_id = ann.id

        self.state = 'annulation'
        self.name = self.annulation_id.name

    def action_comptabilite(self):
        self.state = 'comptable'

    def action_validation(self):
        self.state = 'done'
        self.annulation_id.action_validate()
        if self.total_paiement > 0.0:
            remb = self.env['crm.remboursement'].create({
                'commercial_id': self.commercial_id.id,
                'charge_rembours_id': self.charge_rembours_id.id,
                'date': date.today(),
                'motif': 'Remboursement généré suite a une demande d\'annulation',
                'state': 'open',
                'annulation_id': self.annulation_id.id,
                'reservation_id': self.reservation_id.id,
                'montant_a_rembourser': self.total_paiement,
                'montant_rembourse': 0.0,
                'montant_restant': self.total_paiement,
            })
            self.remboursement_id = remb.id

    # @api.multi
    def action_print(self):
        return self.env.ref('crm_operation.act_report_annulation').with_context(
            {'discard_logo_check': True}).report_action(self.annulation_id.id)

    def action_open_annulation(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.annulation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.annulation_id.id,
            'target': 'current',
        }

    def action_open_reservation(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.reservation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.reservation_id.id,
            'target': 'current',
        }

    def action_open_remboursement(self):
        if self.remboursement_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'crm.remboursement',
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': self.remboursement_id.id,
                'target': 'current',
            }
        else:
            raise UserError(_(u'Aucun document de remboursemenet  n\'a été créé !'))


class CrmDesistementDossierLine(models.Model):
    _name = 'crm.desistement.dossier.line'
    _description = 'dossier desistement'

    name = fields.Char('Num')
    dossier_id = fields.Many2one('crm.desistement.dossier', string='Piece')
    date_depot = fields.Date('Date dépot')
    recu = fields.Boolean('Recu')
    file = fields.Binary('Piece jointe')
    desistement_id = fields.Many2one('crm.desistement', string='Desistement')
    company_id = fields.Many2one('res.company', string=u'Société', related='desistement_id.company_id', store=True)

    # @api.one
    def action_recu(self):
        self.recu = True
        self.date_depot = date.today()

        b = True
        for rec in self.desistement_id.dossier_ids:
            if not rec.recu:
                b = False

        if b:
            self.desistement_id.state = 'dossier'
