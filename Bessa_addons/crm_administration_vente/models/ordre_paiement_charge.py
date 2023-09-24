# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import conversion

from datetime import date


class OrdrePaiementCharge(models.Model):
    _name = 'ordre.paiement.charge'
    _description = 'Ordre de paiement Charge'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('amount')
    def _display_number_to_word(self):
        for rec in self:
            rec.amount_lettre = conversion.conversion(rec.amount)

    name = fields.Char(u'Numéro', required=True, readonly="1", default='/')
    date = fields.Date('Date du paiement', required=True, default=date.today(), readonly=1,
                       states={'open': [('readonly', False)]})
    charge_id = fields.Many2one('charge.annual', string='Référence Charge', required=True, readonly=True)
    product = fields.Many2one(related='charge_id.product', string='Appartement')
    partner_id = fields.Many2one('product.partner', string='Client', readonly=True,
                                 store=True, domain="[('product_id', '=', product)]")
    commercial_id = fields.Many2one(related='charge_id.commercial_id', string='Commercial',
                                    readonly=True,
                                    states={'open': [('readonly', False)]}, store=True)
    partner_reference = fields.Char(related='partner_id.name.ref', string=u'Référence client', readonly=1,
                                    states={'open': [('readonly', False)]}, store=True)
    project_id = fields.Many2one(related='charge_id.project_id', string='Projet', readonly=True,
                                 store=True)
    order_id = fields.Many2one(related='charge_id.order_id', string='Devis', readonly=True, store=True)
    num_dossier = fields.Char(related='charge_id.num_dossier', string=u'N° Dossier', readonly=True,
                              store=True)

    currency_id = fields.Many2one(related='charge_id.currency_id', readonly=True, store=True)
    amount = fields.Monetary('Montant', required=True, readonly=1, states={'open': [('readonly', False)]})
    amount_lettre = fields.Char(compute=_display_number_to_word, string='Montant en lettres', readonly=1)
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement', required=True, readonly=1,
                                       states={'open': [('readonly', False)]})
    objet = fields.Char('Motif de paiement', readonly=1, states={'open': [('readonly', False)]})
    doc_payment_id = fields.Many2one('payment.doc', string=u'Numéro', readonly=1,
                                     states={'open': [('readonly', False)]})
    cheque_domiciliation = fields.Char(related='doc_payment_id.domiciliation', string='Domiciliation', readonly=1,
                                       store=True)
    cheque_ordonateur = fields.Char(related='doc_payment_id.ordonateur', string='Ordonateur', readonly=1, store=True)
    cheque_date = fields.Date(related='doc_payment_id.date', string=u'Date', readonly=1, store=True)
    cheque_objet = fields.Selection(related='doc_payment_id.objet', string='Objet de Chèque', readonly=1, store=True)
    cheque_type = fields.Selection(related='doc_payment_id.type', string='Type de Chèque', readonly=1, store=True)
    observation = fields.Char('Observation')
    state = fields.Selection([('open', 'En instance de paiement'), ('done', u'Terminé'), ('cancel', u'Annulé')])
    type_doc = fields.Selection(related='charge_id.type_doc', store=True)
    payment_id = fields.Many2one('account.payment', string='Payment', compuet='compute_payment',
                                 inverse='payment_inverse', readonly=True)
    type_paiement = fields.Selection([('year', 'Annuel'),
                              ('month', u'Mensuel')], string='Type du paiement',
                             tracking=True)
    duree = fields.Integer(u'Durée')
    year_ids = fields.Many2many('charge.year', string=u'Années', required=True,
                                states={'draft': [('readonly', False)]})
    month_ids = fields.Many2many('charge.month', string=u'Mois',
                                states={'draft': [('readonly', False)]})
    payment_ids = fields.One2many('account.payment', 'order_paiement_id', string='Paiements')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    remise = fields.Boolean(u'Paiement Remise des clés',default=False)

    @api.depends('payment_ids')
    def compute_payment(self):
        if len(self.payment_ids) > 0:
            self.payment_id = self.payment_ids[0]

    def payment_inverse(self):
        if len(self.payment_ids) > 0:
            # delete previous reference
            payment = self.env['account.payment'].browse(self.payment_ids[0].id)
            payment.order_paiement_id = False
        # set new reference
        self.payment_id.order_paiement_id = self

    @api.onchange('partner_id')
    def onchange_partner(self):
        self.cheque_ordonateur = self.partner_id.name.name

    def action_print_recu_paiement(self):
        if self.year_ids:
            year_ids = []
            month_ids = []
            for year in self.year_ids:
                year_ids.append(year.id)
            if self.month_ids:
                for month in self.month_ids:
                    month_ids.append(month.id)
                print(month_ids)
                print(year_ids)
        if self.company_id != self.env.company:
                raise UserError(_(u'Société invalide ! \n\n  Veuillez séléctionner la bonne société !'))
        else:
            view_id = self.env['ir.model.data']._xmlid_to_res_id(
                    'crm_administration_vente.creer_paiement_charge_wizard_form_view')

            return {
                    'name': 'Assistant impression recu de paiement',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': False,
                    'views': [(view_id, 'form'), ],
                    'res_model': 'creer.paiement.charge.wizard',
                    'type': 'ir.actions.act_window',
                    'context': {'default_name': self.id,
                                'default_amount': self.amount,
                                'default_payment_date': self.date,
                                'default_communication': self.objet,
                                'default_doc_payment_id': self.doc_payment_id.id,
                                'default_mode_paiement_id': self.mode_paiement_id.id,
                                'default_partner_reference': self.partner_reference,
                                'default_observation': self.observation,
                                'default_type': self.charge_id.type_doc,
                                'default_name': self.id,
                                'default_type_paiement':self.type_paiement,
                                'default_year_ids':  [(6, 0, year_ids)],
                                'default_month_ids':  [(6, 0, month_ids)],
                                'default_duree':self.duree,
                                'default_remise': self.remise,
                                },
                    'target': 'new',
                }
