# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.tools import conversion
from odoo.exceptions import UserError


class PrintOrdrePaiementWizard(models.TransientModel):
    _name = 'print.ordre.paiement.wizard'

    @api.depends('amount')
    def _display_number_to_word(self):
        for rec in self:
            rec.amount_lettre = conversion.conversion(rec.amount)

    date                 = fields.Date('Date du paiement', required=True, default=date.today())
    order_id             = fields.Many2one('sale.order', string='Commande', required=True, readonly=True)
    echeance_id          = fields.Many2one('crm.echeancier', string='Echeance', readonly=True)
    partner_id           = fields.Many2one(related='order_id.partner_id', string='Client', readonly=True, required=True)
    partner_reference    = fields.Char(u'Référence client')
    project_id           = fields.Many2one(related='order_id.project_id', string='Projet', readonly=True, required=True)
    currency_id          = fields.Many2one(related='order_id.currency_id', readonly=True)
    commercial_id        = fields.Many2one('res.users', string='Commercial', required=True)
    amount               = fields.Monetary('Montant', required=True)
    amount_lettre        = fields.Char(compute=_display_number_to_word, string='Montant en lettres', readonly=1)
    mode_paiement_id     = fields.Many2one('mode.paiement', string='Mode de paiement', required=True)
    objet                = fields.Char('Motif de paiement')
    cheque_num           = fields.Char(u'Numéro')
    cheque_domiciliation = fields.Char('Domiciliation')
    cheque_ordonateur    = fields.Char('Ordonateur')
    cheque_date          = fields.Date(u'Date chèque')
    observation          = fields.Char('Observation')
    cheque_objet = fields.Selection([('normalise', 'NORMALISE'), ('avance', 'AVANCE')], string='Objet de Chèque')
    cheque_type = fields.Selection([('no_certifie', 'NON CERTIFIE'), ('certifie', 'CERTIFIE'), ('credit', 'CHEQUE CREDIT')], string='Type de Chèque')
    state                = fields.Selection([('1', 'operation'), ('2', u'Terminé')], default='1')

    @api.onchange('mode_paiement_id')
    def onchange_mode(self):
        self.cheque_ordonateur = self.partner_id.name

    @api.multi
    def action_print(self):
        self.ensure_one()
        if self.amount <= self.echeance_id.montant_restant:

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

            op = self.env['ordre.paiement'].create({
                'date' : self.date,
                'order_id' : self.order_id.id,
                'echeance_id' : self.echeance_id.id,
                'commercial_id' : self.commercial_id.id,
                'partner_reference' : self.partner_reference,
                'amount' : self.amount,
                'amount_lettre' : self.amount_lettre,
                'mode_paiement_id' : self.mode_paiement_id.id,
                'objet' : self.objet,
                'doc_payment_id' : doc_num,
                'observation' : self.observation,
                'state' : 'open',
            })
            self.state = '2'
            if self.echeance_id:
                self.echeance_id.state = 'inprogress'
            return self.env.ref('crm_echeancier.act_report_ordre_paiement').report_action(op.id)
        else:
            raise UserError(_('Montant superieur au montant prévu pour paiement, veuillez effectué un changement de montant'))
