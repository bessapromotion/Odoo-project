# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import conversion
from odoo.exceptions import UserError

from datetime import date


class PrintOrdrePaiementWizard(models.TransientModel):
    _name = 'print.ordre.paiement.wizard.charge'
    _description = u'Créer ordre de paiement Charge'

    @api.depends('amount')
    def _display_number_to_word(self):
        for rec in self:
            rec.amount_lettre = conversion.conversion(rec.amount)

    date = fields.Date('Date du paiement', required=True, default=date.today())
    charge_id = fields.Many2one('charge.annual', string='Référence Charge', required=True)
    product = fields.Many2one(related='charge_id.product', string='Appartement')
    partner_id = fields.Many2one('product.partner', string='Client',
                                 store=True, domain="[('product_id', '=', product)]")
    commercial_id = fields.Many2one(related='charge_id.commercial_id', string='Commercial', required=True,
                                    readonly=True,
                                    states={'open': [('readonly', False)]})
    currency_id = fields.Many2one(related='charge_id.currency_id', readonly=True)
    partner_reference = fields.Char(related='partner_id.name.ref', string=u'Référence client', readonly=1,
                                    states={'open': [('readonly', False)]})
    project_id = fields.Many2one(related='charge_id.project_id', string='Projet', readonly=True, required=True)
    amount = fields.Monetary('Montant', required=True)
    amount_lettre = fields.Char(compute=_display_number_to_word, string='Montant en lettres', readonly=1)
    mode_paiement_id = fields.Many2one('mode.paiement', string='Mode de paiement', required=True)
    objet = fields.Char('Motif de paiement')
    cheque_num = fields.Char(u'Numéro')
    cheque_domiciliation = fields.Char('Domiciliation')
    cheque_ordonateur = fields.Char('Ordonateur')
    cheque_date = fields.Date(u'Date chèque')
    observation = fields.Char('Observation')
    cheque_objet = fields.Selection([('normalise', 'NORMALISE'), ('avance', 'AVANCE')], string='Objet de Chèque')
    cheque_type = fields.Selection(
        [('no_certifie', 'NON CERTIFIE'), ('certifie', 'CERTIFIE'), ('credit', 'CHEQUE CREDIT')],
        string='Type de Chèque')
    state = fields.Selection([('1', 'operation'), ('2', u'Terminé')], default='1')
    type_paiement = fields.Selection([('year', 'Annuel'),
                                      ('month', u'Mensuel')], string='Type du paiement',
                                     tracking=True)
    duree = fields.Integer(u'Durée')
    year_ids = fields.Many2many('charge.year', string=u'Années', required=True,
                                states={'draft': [('readonly', False)]})
    month_ids = fields.Many2many('charge.month', string=u'Mois',
                                 states={'draft': [('readonly', False)]})
    remise = fields.Boolean(u'Paiement Remise des clés',default=False)

    @api.onchange('mode_paiement_id')
    def onchange_mode(self):
        self.cheque_ordonateur = self.partner_id.name

    # @api.multi
    def action_print(self):
        self.ensure_one()
        if self.amount == 0:
            raise UserError(_(
                u'Le montant doit etre supérieur à 0 '))
        doc = None
        if self.mode_paiement_id.name != 'Espece' and self.cheque_num:
            doc = self.env['payment.doc'].create({
                'name': self.cheque_num,
                'mode_paiement_id': self.mode_paiement_id.id,
                'domiciliation': self.cheque_domiciliation,
                'ordonateur': self.cheque_ordonateur,
                'date': self.cheque_date,
                'objet': self.cheque_objet,
                'type': self.cheque_type,
            })

        if doc:
            doc_num = doc.id
        else:
            doc_num = None

        opc = self.env['ordre.paiement.charge'].create({
            'date': self.date,
            'partner_id': self.partner_id.id,
            'charge_id': self.charge_id.id,
            'commercial_id': self.commercial_id.id,
            'partner_reference': self.partner_reference,
            'amount': self.amount,
            'amount_lettre': self.amount_lettre,
            'mode_paiement_id': self.mode_paiement_id.id,
            'objet': self.objet,
            'doc_payment_id': doc_num,
            'observation': self.observation,
            'state': 'open',
            'duree': self.duree,
            'type_doc': self.charge_id.type_doc,
            'type_paiement': self.type_paiement,
            'year_ids': self.year_ids,
            'month_ids': self.month_ids,
            'remise': self.remise

        })
        self.state = '2'
        return self.env.ref('crm_administration_vente.act_report_ordre_paiement_charge').report_action(opc.id)
