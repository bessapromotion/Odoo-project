# -*- coding: UTF-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import date
from lxml import etree


class ChargeAnnuel(models.Model):
    _name = 'charge.annual'
    _description = 'Charge Annuel '
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    @api.depends('ordre_payment_ids')
    def _nbr_ordres(self):
        for rec in self:
            rec.nbr_ordres = len(rec.ordre_payment_ids)

    @api.depends('payment_ids')
    def _nbr_payments(self):
        for rec in self:
            rec.nbr_payments = len(rec.payment_ids)

    name = fields.Char('Numero')
    reservation_id = fields.Many2one('crm.reservation', string=u'Réservation', required=True,
                                     states={'draft': [('readonly', False)]},
                                     domain="[('company_id', '=', company_id)]")
    order_id = fields.Many2one(related='reservation_id.order_id', required=1, readonly=1,
                               string=u'Réference BC',
                               states={'draft': [('readonly', False)]}, domain="[('state', 'not in', ('cancel', "
                                                                               "'sent', 'draft'))]")
    commercial_id = fields.Many2one(related='reservation_id.commercial_id', string='Commercial', readonly=1, store=True)
    project_id = fields.Many2one(related='reservation_id.project_id', string='Projet', readonly=1,
                                 states={'draft': [('readonly', False)]}, store=True)
    date = fields.Date('Date', required=1,default=lambda self: fields.Date.today(), readonly=1, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Nouveau'),
                              ('valid', u'Validée'), ('cancel', 'Annulé')], string='Etat', default='draft',
                             tracking=True)
    product_ids = fields.One2many(related='reservation_id.product_ids', string='APPARTEMENT', readonly=1,
                                  states={'draft': [('readonly', False)]})
    product_name = fields.Char(related='product_ids.name.name', string=u'Intitulé du bien')
    product = fields.Many2one(related='product_ids.name', string='Appartement', store=True)
    partner_ids = fields.One2many(related='product.partner_ids', string=u'Propriétaires', readonly=1)
    acquereur_id = fields.Many2one('product.partner', string="Acquéreur Actuel",
                                 store=True, domain="[('product_id', '=', product)]")
    num_dossier = fields.Char(related='reservation_id.num_dossier', string=u'N° Dossier', tracking=True, readonly=1,
                              store=True)
    partner_id = fields.Many2one(related='reservation_id.partner_id', string='Réservataire', readonly=1, store=True)
    phone = fields.Char(related='partner_id.phone', string=u'Téléphone', readonly=1, store=True)
    mobile = fields.Char(related='partner_id.mobile', string='Mobile', readonly=1, store=True)
    photo = fields.Binary(related='partner_id.image_1920', string='Photo', store=True)
    # product_ids = fields.One2many(related='reservation_id.product_ids', string='Appartement', readonly=1)
    company_id = fields.Many2one('res.company',string=u'Société', default=lambda self: self.env.company)
    charge_recouv_id = fields.Many2one(related='reservation_id.charge_recouv_id', string=u'Chargé; de recouvrement',
                                       store=True)
    observation = fields.Char(string="Observation")
    # ordre_ids = fields.One2many('ordre.paiement.charge', 'charge_id', string='Ordre de paiement',
    #                             readonly=True,
    #                             domain=[('state', '!=', 'cancel')], store=True)
    currency_id = fields.Many2one('res.currency', string='Devise', store=True,
                                  default=lambda self: self.env.company.currency_id.id)
    type_doc = fields.Selection([('charge', 'Charge'),
                                 ('tag', u'Tag')], string='Type', store=True, tracking=True)
    ordre_payment_ids = fields.One2many('ordre.paiement.charge', 'charge_id', string='Ordres de paiements')
    payment_ids = fields.One2many('account.payment', 'charge_id', string='paiements')
    nbr_ordres = fields.Integer(compute=_nbr_ordres, string='Réservations')
    nbr_payments = fields.Integer(compute=_nbr_payments, string='Réservations')
    orientation = fields.Many2one(related='product.orientation', string=u'Orientation',
                                       store=True)

    @api.model
    def create(self, vals):
        if vals['type_doc'] :
          if vals['type_doc'] == 'charge':
            sequence = 'charge.annual'

          if vals['type_doc'] == 'tag':
            sequence = 'tag.annual'
        else:
            raise UserError(_(u'veuillez selectionner le type du dossier\n\n  charge ou tag'))

        vals['name'] = self.env['ir.sequence'].get(sequence) or '/'
        return super(ChargeAnnuel, self).create(vals)

    # @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le dossier est déjà validé !'))
        else:
            # self.product_ids.unlink()

            rec = super(ChargeAnnuel, self).unlink()
            return rec

    # @api.one
    def action_cancel(self):
        self.state = 'cancel'

    # @api.one
    def action_validate(self):
        self.state = 'valid'
        if self.reservation_id.decision_id.signataire:
            self.acquereur_id.name = self.reservation_id.decision_id.new_partner_id.id
            print(self.acquereur_id.name.etat)
        self.acquereur_id.name.etat = u'Acquéreur'

    @api.onchange('reservation_id')
    def onchange_order(self):
        if self.reservation_id:
            self.partner_id = self.reservation_id.partner_id.id
            self.commercial_id = self.reservation_id.commercial_id.id
            self.project_id = self.reservation_id.project_id.id
            # self.invoice_id     = self.order_id.invoice_ids.id
            self.num_dossier = self.reservation_id.num_dossier

    def action_send_to_payment(self):

        if self.company_id != self.env.company:
            raise UserError(_(u'Société invalide ! \n\n  Veuillez séléctionner la bonne société !'))
        else:

            view_id = self.env['ir.model.data']._xmlid_to_res_id(
                'crm_administration_vente.print_ordre_paiement_wizard_form_view')

            return {
                'name': 'Assistant impression Ordre de paiement des charges',
                'view_mode': 'form',
                'views': [(view_id, 'form'), ],
                'res_model': 'print.ordre.paiement.wizard.charge',
                'type': 'ir.actions.act_window',
                'context': {'default_charge_id': self.id,
                            'default_commercial_id': self.commercial_id.id,
                            'default_date': self.date,
                            'default_type_doc': self.type_doc,
                             'default_product' : self.product.id},
                'target': 'new',
            }

    def action_create_payment(self):
        if self.company_id != self.env.company:
            raise UserError(_(u'Société invalide ! \n\n  Veuillez séléctionner la bonne société !'))
        else:
            print(self.product.id)
            view_id = self.env['ir.model.data']._xmlid_to_res_id(
                'crm_administration_vente.creer_paiement_charge_wizard_direct_form_view')

            return {
                'name': 'Assistant impression recu de paiement directement',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'views': [(view_id, 'form'), ],
                'res_model': 'creer.paiement.charge.wizard.direct',
                'type': 'ir.actions.act_window',
                'context': {'default_charge_id': self.id,
                            'default_payment_date': fields.Date.today(),
                            'default_observation': self.observation,
                            'default_type': self.type_doc,
                            'default_type': self.type_doc,
                            'default_product': self.product.id,
                            },
                'target': 'new',
            }

    #'default_communication': self.objet,
    #'default_doc_payment_id': self.doc_payment_id.id,
    #'default_mode_paiement_id': self.mode_paiement_id.id,
    #'default_partner_reference': self.partner_reference,

    #   Priviléges
    @api.model
    def fields_view_get(self, view_id=None, view_type=None, toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        group_receptionniste = self.env['res.users'].has_group('gestion_profil.group_commercial')
        group_commercial = self.env['res.users'].has_group('gestion_profil.group_commercial')
        group_res_commercial = self.env['res.users'].has_group('gestion_profil.group_res_commercial')
        group_charg_recouvrement = self.env['res.users'].has_group('gestion_profil.group_charg_recouvrement')
        group_res_recouvrement = self.env['res.users'].has_group('gestion_profil.group_res_recouvrement')
        group_adv = self.env['res.users'].has_group('gestion_profil.group_adv')
        group_res_adv = self.env['res.users'].has_group('gestion_profil.group_res_adv')
        group_assistante_adv = self.env['res.users'].has_group('gestion_profil.group_assistante_adv')
        group_comptable_stock = self.env['res.users'].has_group('gestion_profil.group_comptable_stock')
        group_res_compta = self.env['res.users'].has_group('gestion_profil.group_res_compta')
        group_caissier = self.env['res.users'].has_group('gestion_profil.group_caissier')

        doc = etree.XML(res['arch'])
        if group_caissier or group_receptionniste or group_res_commercial or group_commercial or group_charg_recouvrement or group_res_recouvrement or group_assistante_adv or group_comptable_stock or group_res_compta:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('editable', 'none')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')
            res['arch'] = etree.tostring(doc)
        if group_adv or group_res_adv:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '1')
                node.set('create', '1')
                node.set('edit', '1')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '1')
                node.set('editable', 'none')
                node.set('create', '1')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '1')
                node.set('create', '1')
                node.set('edit', '0')
                node.set('delete', '0')

        if group_commercial:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('editable', 'none')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)
        return res
