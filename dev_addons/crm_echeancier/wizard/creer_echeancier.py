# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class CreerEcheancierWizard(models.TransientModel):
    _name = 'creer.echeancier.wizard'
    _description = u'Créer un échéancier'

    # _order = 'hidden_number desc'

    @api.model
    def _first_paiement(self):
        mtn = float(self.amount_total) * float(self.avancement) / 100.0
        return mtn

    name = fields.Many2one('sale.order', required=1, readonly=1, default=lambda self: self.env.context['active_id'])
    currency_id = fields.Many2one(related='name.currency_id')
    project_id = fields.Many2one(related='name.project_id')
    avancement = fields.Integer(related='name.project_id.taux_avancement', string='Taux avancement')

    amount_total = fields.Monetary(related='name.amount_untaxed', string='Total HT', currency_field='currency_id',
                                   readonly=True)
    amount_tva = fields.Monetary(related='name.amount_tax', string='Total TVA', currency_field='currency_id',
                                 readonly=True)
    # residual_signed   = fields.Monetary(related='name.residual_signed', string='Reste a payer', currency_field='currency_id', readonly=True)

    date = fields.Date(u'Date première échéance')  # , required=1)
    number = fields.Integer(u'Nombre échéances')  # , required=1)
    periode = fields.Integer(u'Période en mois')  # , required=1)
    notaire = fields.Boolean(u'Créer une écheance pour le paiement du notaire')
    montant_notaire = fields.Monetary('Montant a payer')

    first_payment = fields.Monetary('Premier versement', currency_field='currency_id', default=lambda self: self._first_paiement())
    date_first_payment = fields.Date('Date premier versement')
    tva = fields.Boolean('creer une echeance pour le paiement de la tva')
    montant_tva = fields.Monetary('Montant TVA', currency_field='currency_id')
    state = fields.Selection(
        [('step1', u'Sélection de la méthode'), ('method1', u'Echéancier manuel'), ('method2', u'Echéancier projet'), ],
        default='step1')
    method = fields.Selection([('step1', 'Sélectionnez une méthode de génération'), ('method1', 'Manuelle'),
                               ('method2', 'Selon l\'avancement du projet'), ], default='step1', string=u'Méthode')
    echeancier_ids = fields.One2many('creer.echeancier.wizard.line', 'wiz_id', string='Echeancier')

    @api.onchange('method')
    def onchange_methode(self):
        self.state = self.method
        if self.state == 'method2':
            if self.project_id.echeancier_ids:
                # self.echeancier_ids.unlink()
                lines = []
                for rec in self.project_id.echeancier_ids:
                    lines.append({
                        'name': rec.name,
                        'taux_av': rec.taux_av,
                        'taux_py': rec.taux_py,
                        'date': rec.date,
                        'amount': self.amount_total * rec.taux_py / 100,
                        'wiz_id': self.id,
                    })
                self.echeancier_ids = lines
            else:
                raise UserError(_('Aucun échéancier n\'est affecté a ce projet, méthode non autorisée ! \n\n  '
                                  'Veuillez créer un échéancier modele pour ce projet ou changer de méthode'))

    @api.onchange('date_first_payment')
    def onchange_date_fp(self):
        if self.date_first_payment:
            dt = self.date_first_payment
            mois = dt.month + 2
            an = 0
            if mois > 12:
                mois = mois - 12
                an = 1
            dt = dt.replace(year=dt.year + an)
            dt = dt.replace(month=mois)
            self.date = dt

    @api.onchange('tva')
    def onchange_tva(self):
        if self.tva:
            self.montant_tva = self.amount_tva

    # @api.multi
    def create_reservation(self):
        if self.name.opportunity_id:
            op = self.name.opportunity_id.id
        else:
            op = None

        res = self.env['crm.reservation'].create({
            'partner_id': self.name.partner_id.id,
            'project_id': self.name.project_id.id,
            'date': date.today(),
            'date_limite': date.today(),
            'commercial_id': self.name.user_id.id,
            'charge_recouv_id': self.name.charge_recouv_id.id,
            'opportunity_id': op,
            'order_id': self.name.id,
            'num_dossier': self.name.num_dossier,
        })

        for rec in self.name.order_line:
            self.env['crm.reservation.product'].create({
                'name': rec.product_id.product_tmpl_id.id,
                'prix_m2': rec.prix_m2,
                'price_2': rec.price_subtotal,
                'reservation_id': res.id,
            })

    def create_methode_1(self):
        if self.number and self.number > 0:
            # echeance pour le premier versement
            self.env['crm.echeancier'].create({
                'name': '#1',
                'order_id': self.name.id,
                'label': 'Le versement intial #1',
                'date_creation': date.today(),
                'date_prevue': self.date_first_payment,
                # 'taux': self.first_payment / self.amount_total,
                'montant_prevu': self.first_payment,
                'type': 'tranche',
                'montant': 0.0,
            })

            # les echeances
            montant_echeance = (self.amount_total - self.first_payment) / self.number
            dt = self.date
            for i in range(1, self.number + 1):
                if i != 1:
                    mois = dt.month + self.periode
                    an = 0
                    if mois > 12:
                        mois = mois - 12
                        an = 1
                    dt = dt.replace(year=dt.year + an)
                    dt = dt.replace(month=mois)

                self.env['crm.echeancier'].create({
                    'name': '#' + str(i + 1),
                    'order_id': self.name.id,
                    'label': 'Paiement tranche #' + str(i + 1),
                    'date_creation': date.today(),
                    'date_prevue': dt,
                    # 'taux'         : 100.0 / self.number,
                    'montant_prevu': montant_echeance,
                    'type': 'tranche',
                    'montant': 0.0,
                })

            if self.tva:
                mois = dt.month + self.periode
                an = 0
                if mois > 12:
                    mois = mois - 12
                    an = 1
                dt = dt.replace(year=dt.year + an)
                dt = dt.replace(month=mois)

                self.env['crm.echeancier'].create({
                    'name': '#' + str(self.number + 2),
                    'order_id': self.name.id,
                    'label': 'Paiement de la TVA #' + str(self.number + 2),
                    'date_creation': date.today(),
                    'date_prevue': dt,
                    'montant_prevu': self.montant_tva,
                    'type': 'tva',
                    'montant': 0.0,
                })

            if self.notaire:
                mois = dt.month + self.periode
                an = 0
                if mois > 12:
                    mois = mois - 12
                    an = 1
                dt = dt.replace(year=dt.year + an)
                dt = dt.replace(month=mois)

                self.env['crm.echeancier'].create({
                    'name': '#' + str(self.number + 3),
                    'order_id': self.name.id,
                    'label': 'Paiement du notaire #' + str(self.number + 3),
                    'date_creation': date.today(),
                    'date_prevue': dt,
                    'montant_prevu': self.montant_notaire,
                    'type': 'notaire',
                    'montant': 0.0,
                })
            return True
        else:
            return False

    def create_methode_2(self):
        if not self.echeancier_ids:
            raise UserError(_('Aucun échéancier n\'est affecté a ce projet, méthode non autorisée ! \n\n  '
                              'Veuillez créer un échéancier modele pour ce projet ou changer de méthode'))

        i = 1
        for rec in self.echeancier_ids:
            if not rec.date or not rec.amount:
                raise UserError(_('Veuillez verifier les données de l\'échéancier ! \n\n  '
                                  'Les dates et les montants doivent etre renseignés'))

            if i == 1:
                # echeance pour le premier versement
                self.env['crm.echeancier'].create({
                    'name': '#1',
                    'order_id': self.name.id,
                    'label': 'Le versement intial #1',
                    'date_creation': date.today(),
                    'date_prevue': rec.date,
                    'montant_prevu': rec.amount,
                    'type': 'tranche',
                    'montant': 0.0,
                })
            else:
                # les echeances
                self.env['crm.echeancier'].create({
                    'name': '#' + str(i),
                    'order_id': self.name.id,
                    'label': 'Paiement tranche #' + str(i),
                    'date_creation': date.today(),
                    'date_prevue': rec.date,
                    # 'taux'         : 100.0 / self.number,
                    'montant_prevu': rec.amount,
                    'type': 'tranche',
                    'montant': 0.0,
                })
            i += 1

        # if self.tva:
        #     mois = dt.month + self.periode
        #     an = 0
        #     if mois > 12:
        #         mois = mois - 12
        #         an = 1
        #     dt = dt.replace(year=dt.year + an)
        #     dt = dt.replace(month=mois)
        #
        #     self.env['crm.echeancier'].create({
        #         'name': '#' + str(self.number+2),
        #         'invoice_id': self.name.id,
        #         'label': 'Paiement de la TVA #' + str(self.number+2),
        #         'date_creation': date.today(),
        #         'date_prevue': dt,
        #         'montant_prevu': self.montant_tva,
        #         'type': 'tva',
        #         'montant': 0.0,
        #     })
        #
        # if self.notaire:
        #     mois = dt.month + self.periode
        #     an = 0
        #     if mois > 12:
        #         mois = mois - 12
        #         an = 1
        #     dt = dt.replace(year=dt.year + an)
        #     dt = dt.replace(month=mois)
        #
        #     self.env['crm.echeancier'].create({
        #         'name': '#' + str(self.number+3),
        #         'invoice_id': self.name.id,
        #         'label': 'Paiement du notaire #' + str(self.number+3),
        #         'date_creation': date.today(),
        #         'date_prevue': dt,
        #         'montant_prevu': self.montant_notaire,
        #         'type': 'notaire',
        #         'montant': 0.0,
        #     })
        return True

    # @api.multi
    def action_appliquer(self):
        if self.state == 'method1':
            result = self.create_methode_1()
        else:
            result = self.create_methode_2()

        if result:
            self.create_reservation()


class CreerEcheancierWizardLine(models.TransientModel):
    _name = 'creer.echeancier.wizard.line'
    _description = 'Echeance'
    # _order = 'date'

    name = fields.Char('Echeance')
    taux_av = fields.Integer('Taux d\'avancement')
    taux_py = fields.Integer('Taux de paiement')
    date = fields.Date('Date echeance', required=1)
    amount = fields.Float('Montant a payer', required=1)
    wiz_id = fields.Many2one('creer.echeancier.wizard', string='Wiz')
