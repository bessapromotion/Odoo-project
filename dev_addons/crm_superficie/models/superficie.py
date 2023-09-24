# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from odoo.tools import conversion
# import datetime
from dateutil import relativedelta


class CrmSuperficie(models.Model):
    _name = 'crm.superficie'
    _description = 'Changement superficie'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    @api.depends('product_ids')
    def _totaux(self):
        for rec in self:
            rec.trop_percu = -1 * sum(line.amount for line in rec.product_ids if line.amount < 0)
            rec.moins_percu = sum(line.amount for line in rec.product_ids if line.amount > 0)
            rec.difference = rec.moins_percu - rec.trop_percu

    @api.depends('product_ids')
    def _nbr_biens(self):
        for rec in self:
            rec.nbr_biens = len(rec.product_ids)

    name = fields.Char(u'Numéro', readonly=1)
    project_id = fields.Many2one('project.project', required=1, string='Projet', readonly=1,
                                 states={'draft': [('readonly', False)]})
    date = fields.Date('Date', required=1, default=date.today(), readonly=1, states={'draft': [('readonly', False)]})
    notes = fields.Text('Notes', readonly=1, states={'draft': [('readonly', False)]})
    product_ids = fields.One2many('crm.superficie.line', 'superficie_id', states={'done': [('readonly', True)]})
    type_bien_ids = fields.Many2many('product.type', string='Type de bien', readonly=1,
                                     states={'draft': [('readonly', False)]})
    nbr_biens = fields.Integer('Nombre de bien', compute=_nbr_biens)
    state = fields.Selection([('draft', 'Nouveau'),
                              ('progress', 'En cours'),
                              ('done', 'Validée'),
                              ('cancel', 'Annulée'), ], string='Etat', default='draft', tracking=True)
    trop_percu = fields.Float(compute=_totaux, string=u'Trop-Perçu')
    moins_percu = fields.Float(compute=_totaux, string=u'Moins-Perçu')
    difference = fields.Float(compute=_totaux, string=u'Difference')
    company_id = fields.Many2one('res.company', u'Société', related='project_id.company_id', store=True)

    def action_load(self):
        view_id = self.env['ir.model.data']._xmlid_to_res_id('crm_superficie.charger_biens_wizard_form_view')

        return {
            'name': 'Charger les biens pour le changement surfaciques',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': False,
            'views': [(view_id, 'form'), ],
            'res_model': 'crm.superficie.charger.bien',
            'type': 'ir.actions.act_window',
            'context': {'default_superficie_id': self.id,
                        'default_project_id': self.project_id.id,
                        },
            'target': 'new',
        }

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('crm.superficie') or '/'

        return super(CrmSuperficie, self).create(vals)

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('Suppression non autorisée ! \n\n  L\'opération est déjà validée !'))
        else:

            rec = super(CrmSuperficie, self).unlink()
            return rec

    def action_cancel(self):
        self.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'

    def action_test(self):
        self.state = 'draft'

    def action_delete_noaction(self):
        for rec in self.product_ids:
            if rec.action == 'noaction':
                rec.unlink()

    def action_validate(self):
        def change_label_2(produit):
            if produit.type_id.name == 'Appartement':
                return produit.project_id.name + ' ' + (produit.type_id.name or ' ') + ' ' + (
                        produit.format_id.name or ' ') + ' Bloc ' + (
                               produit.bloc or '') + ' ' + (produit.etage.name or ' ') + ' Lot ' + (
                               produit.num_lot or ' ') + ' Sup : ' + (str(produit.superficie) or ' ')
            if produit.type_id.name == 'Place de parking':
                return produit.project_id.name + ' Place de parking Bloc ' + (produit.bloc or '') + ' ' + (
                        produit.etage.name or '') + ' Lot ' + (produit.num_lot or '') + ' Num ' + (
                               produit.numero or '')
            if produit.type_id.name == 'Cellier':
                return produit.project_id.name + ' Cellier Bloc ' + (produit.bloc or '') + ' ' + (
                        produit.etage.name or '') + ' Lot ' + (produit.num_lot or '') + ' Num ' + (
                               produit.numero or '')
            if produit.type_id.name == 'Espace a aménager':
                return produit.project_id.name + ' Espace a aménager Bloc' + (produit.bloc or '') + ' ' + (
                        produit.etage.name or '') + ' Lot ' + (produit.num_lot or '') + ' Num ' + (
                               produit.numero or '')
            if produit.type_id.name == 'Local':
                return produit.project_id.name + ' Local Bloc' + (produit.bloc or '') + ' ' + (
                        produit.etage.name or '') + ' Lot ' + (produit.num_lot or '') + ' Num ' + (
                               produit.numero or '') + ' Sup : ' + str(produit.superficie)

            else:
                return produit.name

        for rec in self.product_ids:
            # mise a jour de la fiche produit
            product = rec.name
            product.superficie = rec.superficie_new
            product.num_lot = rec.num_lot
            product.bloc = rec.bloc
            product.etage = rec.etage.id
            product.numero = rec.numero
            product.orientation = rec.orientation.id
            product.type_id = rec.type_id.id
            product.format_id = rec.format_id.id
            product.prix_m2 = rec.prix_m2_new
            product.price_2 = rec.prix_m2_new * rec.superficie_new
            product.list_price = rec.prix_m2_new * rec.superficie_new
            if product.etat == 'Libre':
                product.prix_m2_actuel = rec.prix_m2_new
            product.name = change_label_2(product)
            # moins - perçu
            if rec.amount > 0:
                # mise a jour du devis/commande
                if product.order_id:
                    product.order_id.action_unlock()
                    product.order_id.superficie_id = self.id
                    product.order_id.reservation_ids[0].superficie_id = self.id
                    for o in product.order_id.order_line:
                        if o.product_id.product_tmpl_id.id == product.id:
                            o.superficie = rec.superficie_new
                            o.prix_m2 = rec.prix_m2_new
                            o.name = change_label_2(product)
                            o.price_unit = o.superficie * o.prix_m2
                            # calcul amount
                            total = 0
                            if product.order_id.nbr_echeances > 0:
                                for e in product.order_id.echeancier_ids:
                                    if e.type not in ('tva', 'notaire'):
                                        total += e.montant_prevu
                                # creation échéancier
                                if product.order_id.amount_total != total:  # un control supplémentaire pour éviter de créer une 2eme échéance a 0 DA
                                    self.env['crm.echeancier'].create({
                                        'name': '#MoinsPerçu',
                                        'order_id': product.order_id.id,
                                        'superficie_id': self.id,
                                        'label': 'Tranche complémentaire suite à un changement de superficie (moins perçu) #' + self.name,
                                        'date_creation': date.today(),
                                        'date_prevue': date.today(),
                                        'montant_prevu': product.order_id.amount_total - total,
                                        'type': 'tranche',
                                        'montant': 0.0,
                                    })
                    product.order_id.action_done()
                # mise a jour du reservation

            # trop - perçu
            if rec.amount < 0:
                # mise a jour du devis/commande
                if product.order_id:
                    product.order_id.action_unlock()
                    product.order_id.superficie_id = self.id
                    product.order_id.reservation_ids[0].superficie_id = self.id
                    for o in product.order_id.order_line:
                        if o.product_id.product_tmpl_id.id == product.id:
                            o.superficie = rec.superficie_new
                            o.prix_m2 = rec.prix_m2_new
                            # o.name = change_label(o.name, rec.superficie_new)
                            o.name = change_label_2(product)
                            o.price_unit = o.superficie * o.prix_m2
                            total = 0
                            if product.order_id.nbr_echeances > 0:
                                for e in product.order_id.echeancier_ids:
                                    if e.type not in ('tva', 'notaire'):
                                        total += e.montant_prevu

                                reservation = self.env['crm.reservation'].search(
                                    [('order_id', '=', product.order_id.id), ('state', '=', 'valid')])

                                if product.order_id.amount_total != total:
                                    remb = self.env['crm.remboursement'].create({
                                        'commercial_id': self.env.uid,
                                        'charge_rembours_id': self.env.uid,
                                        'date': date.today(),
                                        'reservation_id': None if not reservation else reservation[0].id,
                                        'motif': 'Remboursement généré suite a une changement de superficie (Trop perçu)',
                                        'state': 'open',
                                        'superficie_id': self.id,
                                        'montant_a_rembourser': total - product.order_id.amount_total,
                                        'montant_rembourse': 0.0,
                                        'montant_restant': total - product.order_id.amount_total,
                                    })
                                    self.env['crm.echeancier'].create({
                                        'name': '#TropPerçu',
                                        'order_id': product.order_id.id,
                                        'superficie_id': self.id,
                                        'remboursement_id': remb.id,
                                        'label': 'Ajustement des échéances (remboursement) suite à un changement de superficie (trop perçu) #' + self.name,
                                        'date_creation': date.today(),
                                        'date_prevue': date.today(),
                                        'montant_prevu': product.order_id.amount_total - total,
                                        'type': 'remboursement',
                                        'montant': 0.0,
                                    })
                    product.order_id.action_done()
        self.state = 'done'


class CrmSuperficieLine(models.Model):
    _name = 'crm.superficie.line'
    _description = 'Ligne changement superficie'

    @api.depends('superficie_new', 'superficie', 'prix_m2', 'prix_m2_new')
    def _amount(self):
        for rec in self:
            rec.amount = (rec.superficie_new * rec.prix_m2_new) - (rec.superficie * rec.prix_m2)

    @api.depends('prix_m2_new', 'superficie_new', 'superficie', 'prix_m2')
    def _prix_m2(self):
        for rec in self:
            rec.price_2 = rec.prix_m2 * rec.superficie
            rec.vente_new = rec.prix_m2_new * rec.superficie_new

    name = fields.Many2one('product.template', string='Bien', readonly=1, required=True)
    superficie = fields.Float('Superficie', readonly=1)
    superficie_new = fields.Float('Nouvelle Superficie')

    prix_m2 = fields.Float('Prix m2', readonly=0)
    prix_m2_new = fields.Float('Nouveau prix m2', readonly=0)
    price_2 = fields.Float(compute=_prix_m2, string='Prix de vente')
    vente_new = fields.Float(compute=_prix_m2, string='Nouveau Prix de vente')
    etat = fields.Selection(related='name.etat', string='Etat du bien')
    state = fields.Selection(related='superficie_id.state', string='Etat')
    order_id = fields.Many2one(related='name.order_id', string='Commande')
    num_dossier = fields.Char(related='name.order_id.num_dossier', string='Num Dossier')
    superficie_id = fields.Many2one('crm.superficie', string='Changement de superficie', readonly=1)
    date = fields.Date(related='superficie_id.date', string='Date')
    action = fields.Selection([('noaction', 'Aucune action'),
                               ('maj', u'Mise à jour fiche produit'),
                               ('moins', u'Création nouvelle échéance'),
                               ('trop', u'Création d\'un remboursement'),
                               ], string=u'Action à faire', compute='action_superficie')
    amount = fields.Float('Difference', compute=_amount)
    company_id = fields.Many2one('res.company', u'Société', related='superficie_id.company_id', store=True)
    # nouvelles infos
    surf_habitable_edd = fields.Float(related='name.surf_habitable_edd', string='Surface habitable(EDD)')
    surf_utile_edd = fields.Float(related='name.surf_utile_edd', string='Surface utile(EDD)')
    surf_habitable_com = fields.Float(related='name.surf_habitable_com', string='Surface habitable(COM)')
    surf_utile_com = fields.Float(related='name.surf_utile_com', string='Surface utile(COM)')

    # nouveaux changements
    partner_id = fields.Many2one(related='name.client_id', string='Client')
    # champ pour les filtres et les groupement
    state_grp = fields.Char('Etat du bien pour groupement', readonly=1)
    bloc_grp = fields.Char('Bloc', readonly=1)
    etage_grp = fields.Char('Etage', readonly=1)

    # champs modifiable
    num_lot = fields.Char(u'N° Lot')
    bloc = fields.Char(u'N° Bloc')
    numero = fields.Char(u'N°')
    etage = fields.Many2one('product.etage', u'N° Etage')
    orientation = fields.Many2one('product.orientation', string='Orientation')
    type_id = fields.Many2one('product.type', string='Type du bien')
    format_id = fields.Many2one('product.format', string='Typologie')

    @api.depends('superficie_new', 'prix_m2_new', 'amount')
    def action_superficie(self):
        for rec in self:
            rec.action = 'noaction'
            if rec.superficie == rec.superficie_new and rec.prix_m2_new == rec.prix_m2:
                rec.action = 'noaction'
            else:
                if rec.etat in ('Libre', 'Bloqué P', 'Bloqué C'):
                    rec.action = 'maj'
                else:
                    if rec.amount > 0:
                        rec.action = 'moins'
                    else:
                        rec.action = 'trop'
