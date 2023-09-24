# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class EcheanceChangeAmoutWizard(models.TransientModel):
    _name = 'echeance.amount.wizard'
    _description = 'Changement montant'
    # _order = 'hidden_number desc'

    name          = fields.Many2one('crm.echeancier', required=1, readonly=1, default=lambda self: self.env.context['active_id'])
    currency_id   = fields.Many2one(related='name.currency_id')
    montant_prevu = fields.Monetary(related='name.montant_restant', store=True)
    amount        = fields.Monetary('Nouveau montant', currency_field='currency_id')
    reste_global  = fields.Monetary('Reste à payer global', currency_field='currency_id', readonly=True)
    msg           = fields.Char('Action', readonly=True)

    @api.onchange('amount')
    def onchange_amount(self):
        amount_diff = self.montant_prevu - self.amount
        if amount_diff != 0.0:
            if amount_diff > 0.0:
                self.msg = 'la difference du montant ' + str(amount_diff) + ' sera ajoutée aux echeances restantes'
            else:
                self.msg = 'la difference du montant ' + str(amount_diff) + ' sera soustraite des echeances restantes'
        else:
            self.msg = ''

    # @api.multi
    def action_appliquer(self):
        amount_diff = self.montant_prevu - self.amount

        if amount_diff != 0.0:  # le nouveau montant est inferieur au montant précedent
            self.name.montant_prevu = self.amount + self.name.montant
            if self.name.montant_restant == 0.0:
                self.name.state = 'done'

            i = 0
            for rec in self.name.order_id.echeancier_ids:
                if rec.state in ('draft', 'open') and rec.id != self.name.id and rec.type == 'tranche':
                    i += 1

            if i != 0:  # il reste encore des echeances
                # le montant a ajouter
                amount_add = amount_diff / i
                for rec in self.name.order_id.echeancier_ids:
                    if rec.state in ('draft', 'open') and rec.id != self.name.id and rec.type == 'tranche':
                        rec.montant_prevu = rec.montant_prevu + amount_add
            else:  # il ne reste aucune echeance, il faut créer une nouvelle
                if amount_diff > 0.0:
                    dt = self.name.date_prevue
                    mois = dt.month + 2
                    an = 0
                    if mois > 12:
                        mois = mois - 12
                        an = 1
                    dt = dt.replace(year=dt.year + an)
                    dt = dt.replace(month=mois)

                    self.env['crm.echeancier'].create({
                        'name'         : self.name.name + '+',
                        'order_id'   : self.name.order_id.id,
                        'label'        : 'Paiement reportée de la tranche ' + self.name.name,
                        'date_creation': date.today(),
                        'date_prevue'  : dt,
                        'type'         : 'tranche',
                        'montant_prevu': amount_diff,
                        'montant'      : 0.0,
                    })
                else:
                    raise UserError(_('Trop Percu  ! \n\n  Le nouveau montant depasse le reste à payer !'))

    # @api.multi
    def action_appliquer2(self):
        amount_diff = self.amount - self.montant_prevu

        if amount_diff != 0.0:  # le nouveau montant est superieur au montant précedent
            self.name.montant_prevu = self.amount + self.name.montant
            if self.name.montant_restant == 0.0:
                self.name.state = 'done'

            lst = self.env['crm.echeancier'].search([('order_id', '=', self.name.order_id.id),
                                                     ('state', 'in', ('draft', 'open')),
                                                     ('type', '!=', 'remboursement'),
                                                     ])
                                                     # ('id', '!=', self.name.id)])
            # verifier si le montant a payer dépasse le montant global (reste a payer)
            mtn_total = sum(line.montant_restant for line in lst) - amount_diff
            if mtn_total < self.amount:
                raise UserError(_('Trop Percu  ! \n\n  Le nouveau montant dépasse le reste à payer global !'))

            for rec in lst:
                if rec.id != self.name.id:
                    if amount_diff > 0:
                        if amount_diff >= rec.montant_restant:
                            amount_diff = amount_diff - rec.montant_prevu + rec.montant
                            rec.montant_prevu = rec.montant
                            if rec.montant == 0.0:
                                rec.state = 'cancel'
                                rec.observation = 'Tranche annulée, payée lors du paiement de la tranche #' + self.name.name
                            else:
                                rec.state = 'done'
                                rec.observation = 'Tranche cloturée, payée lors du paiement de la tranche #' + self.name.name
                        else:
                            rec.montant_prevu = rec.montant_restant - amount_diff
                            amount_diff = 0
                    elif amount_diff < 0:
                        rec.montant_prevu = amount_diff * -1 + rec.montant_prevu
                        amount_diff = 0

            if amount_diff != 0:  # traitement de toutes les echeances et il reste encore un montant
                dt = self.name.date_prevue
                mois = dt.month + 2
                an = 0
                if mois > 12:
                    mois = mois - 12
                    an = 1
                dt = dt.replace(year=dt.year + an)
                dt = dt.replace(month=mois)

                self.env['crm.echeancier'].create({
                    'name'         : self.name.name + '+',
                    'order_id'   : self.name.order_id.id,
                    'label'        : 'Paiement reportée de la tranche ' + self.name.name,
                    'date_creation': date.today(),
                    'date_prevue'  : dt,
                    'type'         : 'tranche',
                    'montant_prevu': abs(amount_diff),
                    'montant'      : 0.0,
                })
            # else:
            #     raise UserError(_('Trop Percu  ! \n\n  Le nouveau montant depasse le reste a payer !'))
