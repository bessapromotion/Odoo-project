# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import date


class CrmDesistement(models.Model):
    _name = 'crm.desistement'
    _inherit = 'crm.desistement'

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
    company_id = fields.Many2one('res.company', u'Société', related='reservation_id.project_id.company_id', store=True)
    type_annulation = fields.Selection([('desistement', 'desistement'),
                                        ('annulation', 'Annulation')], string='Type d\'annulation', required=True,
                                       tracking=True,
                                       default='desistement')
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('desistement') or '/'
        record = super(CrmDesistement, self).create(vals)
        return record

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
        # self.annulation_id.action_validate()
        self.state = 'annulation'
        self.name = self.annulation_id.name
