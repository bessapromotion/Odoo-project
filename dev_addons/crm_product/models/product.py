# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductType(models.Model):
    _name = 'product.type'
    _description = 'Type'

    name = fields.Char('Type')


class ProductTypeAppt(models.Model):
    _name = 'product.type.appt'
    _description = 'Type Appartement'

    name = fields.Char('Type')


class ProductEnsoleillement(models.Model):
    _name = 'product.ensoleillement'
    _description = 'Type Ensoleillement'

    name = fields.Char('Type')
    note = fields.Float('Note')
    coef = fields.Float('Coef', default=1)


class ProductVis(models.Model):
    _name = 'product.vis'
    _description = 'Type Vis-à-vis'

    name = fields.Char('Type')
    note = fields.Float('Note')
    coef = fields.Float('Coef', default=1)


class ProductFormat(models.Model):
    _name = 'product.format'
    _description = 'Format'

    name = fields.Char('Type', help='F3, F4, F5...')


class ProductOrientation(models.Model):
    _name = 'product.orientation'
    _description = 'Orientation'

    name = fields.Char('Orientation')
    note = fields.Float('Note')
    coef = fields.Float('Coef', default=1)


class ProductSuperficieType(models.Model):
    _name = 'product.superficie.type'
    _description = 'Superficie type'

    name = fields.Char('Superficie')
    note = fields.Float('Note')
    coef = fields.Float('Coef', default=1)


class ProductAgencementType(models.Model):
    _name = 'product.agencement.type'
    _description = 'Agencement type'

    name = fields.Char('Agencement')
    note = fields.Float('Note')
    coef = fields.Float('Coef', default=1)


class ProductEtage(models.Model):
    _name = 'product.etage'
    _description = 'Etage'

    name = fields.Char('Etage')
    note = fields.Float('Note')
    coef = fields.Float('Coef', default=1)


class ProductEtageType(models.Model):
    _name = 'product.etage.type'
    _description = 'Type Etage'

    name = fields.Char('Type Etage')
    note = fields.Float('Note')
    coef = fields.Float('Coef', default=1)


class ProductDifficulteType(models.Model):
    _name = 'product.difficulte.type'
    _description = 'Type de dificulté de vente'

    name = fields.Selection([('difficile', 'Difficile à vendre'),
                             ('vendable', 'Vendable'),
                             ('facile', 'Facile à vendre'),
                             ('tres_facile', 'Tres facile à vente'),
                             ], string='Difficulté')
    min = fields.Float('Min')
    max = fields.Float('Max')


class ProductPositionnement(models.Model):
    _name = 'product.positionnement'
    _description = 'Type Positionnement'

    name = fields.Selection([('bon', 'Bon'),
                             ('moyen', 'Moyen'),
                             ('mauvais', 'Mauvais')], string='Positionnement')
    note = fields.Float('Note')
    coef = fields.Float('Coef', default=1)
    vis_id = fields.Many2one('product.vis', string='Vis-à-vis', )
    ensoleillement_id = fields.Many2one('product.ensoleillement', string='Ensoleillement', )


class Product(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    @api.constrains('purchase_ok', 'sale_ok')
    def _check_purchase_sale_ok(self):
        for rec in self:
            if rec.sale_ok and rec.purchase_ok:
                raise ValidationError(
                    _("Le produit doit être achetable ou vendable."))

    @api.depends('superficie', 'prix_m2')
    def compute_price(self):
        for rec in self:
            rec.price_2 = rec.superficie * rec.prix_m2
            rec.list_price = rec.price_2

    bloc = fields.Char('Bloc')
    type_id = fields.Many2one('product.type', string='Type du bien')
    orientation = fields.Many2one('product.orientation', string='Orientation')
    format_id = fields.Many2one('product.format', string='Typologie')
    etage = fields.Many2one('product.etage', string='Etage')
    niveau = fields.Float('Niveau', default=0.0)
    numero = fields.Char(u'Numéro')
    superficie = fields.Float('Superficie', default=1)
    surf_habitable_edd = fields.Float('Surface habitable(EDD)')
    surf_utile_edd = fields.Float('Surface utile(EDD)')
    surf_habitable_com = fields.Float('Surface habitable(COM)')
    surf_utile_com = fields.Float(related='superficie', string='Surface utile(COM)')
    num_lot = fields.Char('N° Lot')
    prix_m2 = fields.Float('Prix m2')
    prix_m2_actuel = fields.Float('Prix Actuel m2')
    project_id = fields.Many2one(
        'project.project', string='Project',)
    project_name = fields.Char(related='project_id.name', store=True, string='Projetname')
    price_2 = fields.Float(compute=compute_price, string='Prix de vente', readonly=1)
    client_id = fields.Many2one('res.partner', string='Client', readonly=1)
    etat = fields.Selection([('Libre', 'Libre'),
                             ('Pré-Réservé', 'Pré-Réservé'),
                             ('Réservé', 'Réservé'),
                             ('Livré', 'Livré'),
                             ('Bloqué P', 'Bloqué P'),
                             ('Bloqué C', 'Bloqué C'), ], string='Etat du bien')
    order_id = fields.Many2one('sale.order', string='Devis retenu', readonly=True)
    plan_pdf = fields.Binary('Plan')
    plan_1_pdf = fields.Binary(related='plan_pdf', string='Plan', readonly=True)

    line_ids = fields.One2many('sale.order.line', 'product_tmpl_id2', string='Pré-réservation en cours',
                               domain=[('state', '!=', 'cancel')])
    line_canceled_ids = fields.One2many('sale.order.line', 'product_tmpl_id2', string='Pré-réservation annulée',
                                        domain=[('state', '=', 'cancel')])
    view_orders = fields.Boolean('Afficher le detail', default=False)

    @api.depends('type_etage_id', 'superficie_id', 'orientation', 'agencement_id')
    def compute_note_appt(self):
        for rec in self:
            if (rec.type_etage_id.coef + rec.orientation.coef + rec.superficie_id.coef + rec.agencement_id.coef) != 0:
                rec.note_appt = (
                                        rec.type_etage_id.note * rec.type_etage_id.coef + rec.orientation.note * rec.orientation.coef + rec.superficie_id.note * rec.superficie_id.coef + rec.agencement_id.note * rec.agencement_id.coef) / (
                                        rec.type_etage_id.coef + rec.orientation.coef + rec.superficie_id.coef + rec.agencement_id.coef)
            else:
                rec.note_appt = 0
            rec.type_difficulte = ''
            note = self.env['product.difficulte.type'].search(
                [('min', '<=', rec.note_appt), ('max', '>', rec.note_appt)])
            if note:
                rec.type_difficulte = note[0].name

    @api.depends('vis_id', 'ensoleillement_id')
    def get_tyep_positionnement(self):
        for rec in self:
            rec.positionnement_id = False
            p = self.env['product.positionnement'].search(
                [('vis_id', '=', self.vis_id.id), ('ensoleillement_id', '=', self.ensoleillement_id.id)])
            if p:
                rec.positionnement_id = p

    commune_id = fields.Many2one('res.commune', string='Commune', )
    type_appt_id = fields.Many2one('product.type.appt', string='Type appartement', )
    ensoleillement_id = fields.Many2one('product.ensoleillement', string='Ensoleillement', )
    vis_id = fields.Many2one('product.vis', string='Vis-à-vis', )
    superficie_id = fields.Many2one('product.superficie.type', string='Superficie', )
    agencement_id = fields.Many2one('product.agencement.type', string='Agencement', )
    type_etage_id = fields.Many2one('product.etage.type', string='Type Etage', )
    positionnement_id = fields.Many2one('product.positionnement', string='Positionnement',
                                        compute='get_tyep_positionnement', store=True)
    note_appt = fields.Float(string='Note appartement', compute='compute_note_appt', store=True)
    type_difficulte = fields.Char(string='Type de dificulté de vente', store=True, compute='compute_note_appt', )


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    line_ids = fields.One2many('sale.order.line', 'product_id', string='Pré-réservation en cours',
                               domain=[('state', '!=', 'cancel')])
