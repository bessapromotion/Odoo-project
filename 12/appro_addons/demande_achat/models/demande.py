from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import UserError


class Project(models.Model):
    _inherit    = 'project.project'

    stock_destination_id = fields.Many2one('stock.location', string='Emplacement Stock')


class Purchase(models.Model):
    _inherit    = 'purchase.order'

    project_id = fields.Many2one('project.project', string='Projet')


class DemandeAchat(models.Model):
    _name    = 'demande.achat'
    _inherit = ['mail.thread']
    _description = 'Demande d\'achat'
    _order = "name desc"

    @api.multi
    @api.depends('affet_ids')
    def _nbr_doc(self):
        for rec in self:
            af = 0
            for line in rec.affet_ids:
                if line.state != 'cancel':
                    af += 1
            rec.nbr_affectation = af

    @api.depends('has_requisition')
    def _has_requisition(self):
        for rec in self:
            if rec.has_requisition:
                rec.nbr_requisition = 1
            else:
                rec.nbr_requisition = 0

    def _get_default_location(self):
        loc = self.env['stock.location'].search([('usage', '=', 'internal'), ('name', '=', 'Stock'), ('location_id', '=', 11)])
        if loc.exists():
            return loc[0].id
        else:
            return None

    name           = fields.Char(u'Numéro', default='/', readonly=1)
    objet          = fields.Char('Objet de la demande')
    user_id        = fields.Many2one('res.users', 'Utilisateur', default=lambda self: self.env.user.id)
    employe_id     = fields.Many2one('hr.employee', 'Demandeur', required=True, readonly=1, states={'new': [('readonly', False)]}, track_visibility='onchange')
    employe_glb_id = fields.Many2one('hr.employee', 'Demandeur')
    department_id  = fields.Many2one('hr.department', 'Service demandeur', required=True, readonly=1, states={'new': [('readonly', False)]}, track_visibility='onchange')
    department_glb_id  = fields.Many2one('hr.department', 'Service demandeur')
    project_id     = fields.Many2one('project.project', string='Projet', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    ddate          = fields.Date('Date demande', default=date.today(), required=True, readonly=1, states={'new': [('readonly', False)]}, track_visibility='onchange')
    location_id    = fields.Many2one('stock.location', string='Stock', default=_get_default_location, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    stock_destination_id = fields.Many2one('stock.location', string='Stock destination', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    destination = fields.Selection([('demandeur', 'Livrer au demandeur'),
                                    ('stock', u'Entrée en stock'),
                                    ('entrepot', u'Transfert vers un dépôt'),
                                    ], string='Destination', default='demandeur', help=u'Quelle est la destination des produits demandés', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    date_appro     = fields.Date('Date Appro.', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    date_prevue    = fields.Date(u'Date prévue', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    responsable_id = fields.Many2one('res.users', 'Responsable', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    state          = fields.Selection([('new', 'Nouvelle'),
                                       ('soumis', 'Validation'),
                                       ('stock', 'Verification stock'),
                                       ('service', 'Service'),
                                       ('done', u'Traitée'),
                                       ('cancel', u'Annulée')], string='Etat', default='new', track_visibility='onchange')
    line_ids       = fields.One2many('demande.achat.line', 'demande_id', string='Lignes demande', readonly=1, states={'new': [('readonly', False)], 'stock': [('readonly', False)]})
    line_service_ids = fields.One2many('demande.achat.service.line', 'demande_id', string='Lignes demande', readonly=1, states={'new': [('readonly', False)]})
    # appro_ids      = fields.One2many('demande.appro', 'demande_id', string='Demande d\'achat')
    affet_ids      = fields.One2many('stock.picking', 'demande_id', string='Mise a disposition')
    observation    = fields.Text('Observation')
    nbr_affectation = fields.Integer(compute=_nbr_doc, string='Nombre d\'affectations')
    # nbr_appro      = fields.Integer(compute=_nbr_doc, string='Nombre de demande d\'achat')
    nbr_requisition = fields.Integer(compute=_has_requisition, string='A une consultation')
    has_requisition = fields.Boolean('A une consultation')
    motif_refus    = fields.Text('Motif de refus')
    dem_global     = fields.Boolean('Demande Globale')
    type_demande   = fields.Selection([('achat', 'Stockable'), ('service', 'Service')], string='Type demande', required=True, default='achat', readonly=1, states={'new': [('readonly', False)]})
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.user.company_id)

    @api.onchange('project_id')
    def onchange_project(self):
        self.stock_destination_id = self.project_id.stock_destination_id.id

    @api.multi
    def unlink(self):
        if self.state != 'new':
            raise UserError(_(u'Suppression non autorisée ! \n\n  La demande est déjà envoyée pour validation ! \n\n Utilisez la fonction d\'annulation'))
        else:
            self.line_ids.unlink()
            rec = super(DemandeAchat, self).unlink()
            return rec

    @api.model
    def create(self, vals):
        vals['name'] = '/'
        if vals['employe_glb_id']:
            vals['employe_id'] = vals['employe_glb_id']
        if vals['department_glb_id']:
            vals['department_id'] = vals['department_glb_id']
        # if vals['site_glb_id']:
        #     vals['site_id'] = vals['site_glb_id']

        if vals['state'] == 'stock':
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].get('demande.achat') or '/'

        return super(DemandeAchat, self).create(vals)

    @api.onchange('employe_id')
    def onchange_employe(self):
        if self.employe_id:
            self.department_id = self.employe_id.department_id.id
            # self.site_id = self.employe_id.site_id.id

    @api.onchange('employe_glb_id')
    def onchange_employe_global(self):
        if self.employe_glb_id:
            self.department_glb_id = self.employe_glb_id.department_id.id
            # self.site_glb_id = self.employe_glb_id.site_id.id

            self.employe_id = self.employe_glb_id.id
            self.department_id = self.department_glb_id.id
            # self.site_id = self.site_glb_id.id

    @api.onchange('department_glb_id')
    def onchange_department_global(self):
        if self.department_glb_id:
            self.department_id = self.department_glb_id.id

    # @api.onchange('site_glb_id')
    # def onchange_site_global(self):
    #     if self.site_glb_id:
    #         self.site_id = self.site_glb_id.id

    def num_document(self):
        if self.name == '/':
            self.name = self.env['ir.sequence'].get('demande.achat') or '/'

    @api.one
    def action_send_to_validation(self):
        # numérotation de la campagne
        if len(self.line_ids) + len(self.line_service_ids) > 0:
            self.num_document()
            self.state = 'soumis'
            for rc in self.line_ids:
                rc.state = 'waiting'

            for rc in self.line_service_ids:
                rc.state = 'waiting'
        else:
            raise UserError(_(
                u'Veuillez saisir la liste des produits demandés avant envoi à la validation'))

    @api.multi
    def action_valider_tout(self):
        if self.type_demande == 'achat':
            for rc in self.line_ids:
                rc.state = 'to_purchase'
        else:
            for rc in self.line_service_ids:
                rc.state = 'to_purchase'

        self.action_verification_stock()

    @api.multi
    def action_refuser_tout(self):
        self.state = 'cancel'
        for rc in self.line_ids:
            rc.state = 'refus'

    @api.one
    def action_verification_stock(self):
        ready_for_verif_stock_ok = True
        if self.type_demande == 'achat':
            for rc in self.line_ids:
                if rc.state == 'waiting':
                    ready_for_verif_stock_ok = False
                    break
        else:
            for rc in self.line_service_ids:
                if rc.state == 'waiting':
                    ready_for_verif_stock_ok = False
                    break
                if not rc.product_id:
                    raise UserError(
                        _(u'Veuillez sélectionner les produits dans la liste des besoins'))

        if ready_for_verif_stock_ok:
            if self.type_demande == 'achat':
                self.state = 'stock'
            else:
                self.state = 'service'
        else:
            raise UserError(_(u'Certains produits ne sont pas validés ou annulés, veuillez les completer avant d\'envoyer pour la verification stock'))

    @api.one
    def action_encours(self):
        if self.responsable_id:
            self.state = 'stock'
        else:
            raise UserError(_('Veuillez assigner cette demande pour son traitement'))

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    def get_picking_id(self, type_operation):
        picking = self.env['stock.picking'].search([('picking_type_id', '=', type_operation.id), ('demande_id', '=', self.id), ])
        if picking.exists():
            return picking[0].id
        else:
            res_model, loc_id = self.env['ir.model.data'].get_object_reference('demande_achat', 'location_mad')
            picking = self.env['stock.picking'].create({
                'user_id': self.user_id.id,
                'employe_id': self.employe_id.id,
                'department_id': self.department_id.id,
                # 'partner_id': self.site_id.id,
                'demande_id': self.id,
                'state': 'draft',
                'origin': self.name,
                'picking_type_id': type_operation.id,
                'move_type': 'direct',
                'company_id': self.company_id.id,
                'create_uid': self.user_id.id,
                'create_date': datetime.now(),
                'write_uid': self.user_id.id,
                'write_date': datetime.now(),
                'min_date': datetime.now(),
                'max_date': datetime.now(),
                'printed': False,
                'location_dest_id': loc_id,
                'location_id': type_operation.default_location_src_id.id,
            })
            return picking[0].id

    def get_type_operation(self, location):
        type_move = self.env['stock.picking.type'].search([('default_location_src_id', '=', location), ('mise_a_dispo', '=', 'mad'), ])
        # type_move = self.env['stock.picking.type'].search([('default_location_src_id', '=', location), ('code', '=', 'internal') ])
        if type_move.exists():
            return type_move[0]
        else:
            return None

    @api.one
    def action_create_doc_affectation2(self, ok_affect):
        if ok_affect:
            for rc in self.line_ids:
                if (rc.qty_dispo > 0 or rc.qty_achat > 0) and rc.state in ('to_purchase', 'dispo'):
                    res_model, loc_id = self.env['ir.model.data'].get_object_reference('demande_achat', 'location_mad')
                    type_operation = self.get_type_operation(rc.location_id.id)
                    if type_operation:
                        picking = self.get_picking_id(type_operation)
                        self.env['stock.move'].create({
                            'product_id': rc.product_id.id,
                            'name': rc.product_id.name,
                            'origin': self.name,
                            'create_uid': self.user_id.id,
                            'create_date': datetime.now(),
                            'write_uid': self.user_id.id,
                            'write_date': datetime.now(),
                            'product_uom': rc.product_id.product_tmpl_id.uom_id.id,
                            'product_uom_qty': rc.qty,
                            'procure_method': 'make_to_stock',
                            'picking_type_id': type_operation.id,
                            'location_id': type_operation.default_location_src_id.id,
                            'sequence': 10,
                            'company_id': self.company_id.id,
                            'state': 'draft',
                            # 'ordred_qty': rc.qty,
                            # 'date_expected': datetime.now(),
                            # 'partially_available': False,
                            # 'propagate': True,
                            'location_dest_id': loc_id,
                            'date': datetime.now(),
                            'scrapped': False,
                            'picking_id': picking,
                        })
                    else:
                        raise UserError(_(
                            u'Aucun mouvement Transfert interne n\'est créé. veuillez le créer en positionnant le champs (Opération interne) a Mise a disposition'))

    # @api.one
    # def action_create_demande_appro(self, doc_achat=True):
    #     # creer le doc achat
    #     if doc_achat:
    #         nbr_line = 0
    #
    #         appro = self.env['demande.appro'].create({
    #             'name'           : '/',
    #             'user_id'        : self.user_id.id,
    #             'employe_id'     : self.employe_id.id,
    #             'department_id'  : self.department_id.id,
    #             'demande_id'     : self.id,
    #             'date_prevue'    : self.date_prevue,
    #             'responsable_id' : self.responsable_id.id,
    #             # 'site_id'        : self.site_id.id,
    #             'state'          : 'new',
    #         })
    #
    #         if self.type_demande == 'achat':
    #             for rc in self.line_ids:
    #                 if rc.qty_achat > 0 and rc.state == 'to_purchase':
    #                     self.env['demande.appro.line'].create({
    #                         'name'       : str(nbr_line+1),
    #                         'product_id' : rc.product_id.id,
    #                         'description': rc.product_id.name,
    #                         'qty'        : rc.qty_achat,
    #                         'appro_id'   : appro.id,
    #                     })
    #                     nbr_line += 1
    #         else:
    #             for rc in self.line_service_ids:
    #                 if rc.qty > 0 and rc.state == 'to_purchase':
    #                     self.env['demande.appro.line'].create({
    #                         'name'       : str(nbr_line+1),
    #                         'product_id' : rc.product_id.id,
    #                         'description': rc.product_id.name,
    #                         'qty'        : rc.qty,
    #                         'appro_id'   : appro.id,
    #                     })
    #                     nbr_line += 1
    #
    #     return True

    @api.one
    def action_create_ao(self, doc_achat=True):
        # Créer le convention
        if doc_achat or self.type_demande == 'service':
            self.has_requisition = True

            consult = self.env['purchase.requisition'].create({
                'name'          : self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender'),
                'user_id'       : self.responsable_id.id,
                'type_id'       : 2,
                'demande_id'    : self.id,
                'schedule_date' : self.date_prevue,
                'state'         : 'in_progress',
                'origin'        : self.name,
                'company_id'    : self.company_id.id,
            })

            if self.type_demande == 'achat':
                for rc in self.line_ids:
                    if rc.qty_achat > 0 and rc.state == 'to_purchase':
                        self.env['purchase.requisition.line'].create({
                            # 'name'       : str(nbr_line+1),
                            'product_id' : rc.product_id.id,
                            'product_qty': rc.qty_achat,
                            'product_uom_id': rc.product_id.uom_id.id,
                            # 'des/cription': rc.product_id.name,
                            'requisition_id'   : consult.id,
                            'schedule_date'   : self.date_prevue,
                        })
            else:
                for rc in self.line_service_ids:
                    if rc.qty > 0 and rc.state == 'to_purchase':
                        self.env['purchase.requisition.line'].create({
                            # 'name'       : str(nbr_line+1),
                            'product_id' : rc.product_id.id,
                            'product_qty': rc.qty,
                            'product_uom_id': rc.product_id.uom_id.id,
                            # 'des/cription': rc.product_id.name,
                            'requisition_id'   : consult.id,
                            'schedule_date'   : self.date_prevue,
                        })

    def action_demande_wizard(self):
        doc_achat = False
        doc_affect = False

        if self.type_demande == 'achat':
            for rc in self.line_ids:
                if rc.state in ('new', 'waiting', 'valid'):
                    raise UserError(_(u'Veuillez positionner l\'état de disponibilité des produits avant de créer les documents'))
                else:
                    if rc.state not in ('cancel', 'refus', 'done'):
                        if not rc.product_id:
                            raise UserError(_(u'Veuillez sélectionner les produits pour chaque ligne pour lancer la création des documents'))
                        else:
                            if rc.state in ('error', ):
                                raise UserError(_(u'Le produit de la ligne (erreur) n\'a pas d\'emplacement stock par défaut. Veuillez verifier cette information dans la catégorie du produit, puis revérifier sa disponibilité'))
                            else:
                                if rc.qty_dispo > 0 or rc.qty_achat > 0:
                                    doc_affect = True

                                if rc.qty_achat > 0:
                                    doc_achat = True
        else:
            for rc in self.line_service_ids:
                if rc.state in ('new', 'waiting', 'valid'):
                    raise UserError(_(u'Veuillez positionner l\'état de disponibilité des produits avant de créer les documents'))
                else:
                    if rc.state not in ('cancel', 'refus', 'done'):
                        if not rc.product_id:
                            raise UserError(_(u'Veuillez sélectionner les produits pour chaque ligne pour lancer la création des documents'))
                        else:
                            if rc.qty > 0:
                                doc_achat = True
        if self.destination == 'stock':
            doc_affect = False

        self.env['purchase.create.document.wizard'].create({})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.create.document.wizard',
            'type': 'ir.actions.act_window',
            'context' : {'default_demande_id': self.id,
                         'default_destination': self.destination,
                         'default_stock_destination_id': self.stock_destination_id.id or None,
                         'default_achat': doc_achat,
                         'default_affect': doc_affect,
                         'default_type_demande': self.type_demande,
                         },
            'target': 'new',
            'res_id': False,
        }

    def action_create_document(self):
        # check lines
        doc_affect = False
        doc_achat  = False
        if self.type_demande == 'achat':
            for rc in self.line_ids:
                if rc.state in ('new', 'waiting', 'valid'):
                    raise UserError(_(
                        u'Veuillez positionner l\'état de disponibilité des produits avant de créer les documents'))
                else:
                    if rc.state not in ('cancel', 'refus', 'done'):
                        if not rc.product_id:
                            raise UserError(_(
                                u'Veuillez sélectionner les produits pour chaque ligne pour lancer la création des documents'))
                        else:
                            if rc.state in ('error', ):
                                raise UserError(_(
                                    u'Le produit de la ligne (erreur) n\'a pas d\'emplacement stock par defaut. Veuillez verifier cette information dans la categorie du produit, puis reverifier sa disponibilité'))
                            else:
                                if rc.qty_dispo > 0 or rc.qty_achat > 0:
                                    doc_affect = True

                                if rc.qty_achat > 0:
                                    doc_achat = True

            self.action_create_doc_affectation2(doc_affect)
        # self.action_create_demande_appro(doc_achat)
        self.action_create_ao(doc_achat)
        self.state = 'done'
        return True

    @api.one
    def reverifie_stock(self):
        for rec in self.line_ids:
            rec.onchange_product()
            rec.onchange_qty()


class DemandeAchatLine(models.Model):
    _name = 'demande.achat.line'
    _description = 'Ligne demande achat'

    # @api.one
    # @api.depends('partner_ids')
    # def _nbr_partner(self):
    #     self.nbr_partner = len(self.partner_ids)

    description = fields.Char('Description de la demande', required=True)
    qty         = fields.Float(u'Quantité demandée', default=1)
    qty_dispo   = fields.Float(u'Quantité disponible', default=0)
    qty_achat   = fields.Float(u'Quantité à acheter')
    product_id  = fields.Many2one('product.product', string='Produit')
    uom_id  = fields.Many2one(related='product_id.uom_id', string=u'Unité', readonly=True)
    demande_id  = fields.Many2one('demande.achat', string='Demande')
    location_id = fields.Many2one(related='demande_id.location_id', string='Stock')
    dem_global  = fields.Boolean(related='demande_id.dem_global', string='Demande globale')
    # partner_ids = fields.Many2many('res.partner', string='Fournisseurs', readonly=1, states={'to_purchase': [('readonly', False)]})
    # nbr_partner = fields.Integer(compute=_nbr_partner, string='Nombre de fournisseurs')

    state       = fields.Selection([('new', 'Nouvelle'),
                                    ('waiting', 'en attente'),
                                    ('valid', u'Validée'),
                                    ('refus', u'Refusée'),
                                    ('dispo', 'Disponible'),
                                    ('error', 'Erreur'),
                                    ('to_purchase', 'A acheter'),
                                    ('done', u'Traitée'),
                                    ('cancel', u'Annulée')], default='new', string='Etat')
    observation = fields.Char('Observation')

    # @api.onchange('qty_dispo')
    # def occhange_qty_dispo(self):
    #     self.qty_achat = self.qty - self.qty_dispo
    #     if self.qty <= self.qty_dispo:
    #         self.state = 'dispo'
    #         self.qty_achat = 0
    #     if self.qty_achat >= 1:
    #         self.state = 'to_purchase'

    @api.onchange('qty', 'qty_dispo')
    def onchange_qty(self):
        self.qty_achat = self.qty - self.qty_dispo
        if self.qty <= self.qty_dispo:
            self.state = 'dispo'
            self.qty_achat = 0
        if self.qty_achat >= 1:
            self.state = 'to_purchase'

    @api.onchange('location_id')
    def onchange_location(self):
        if self.location_id and self.product_id:
            req = 'select sum(quantity) as qty from stock_quant where product_id=%s and location_id=%s;'
            rub = (self.product_id.id, self.location_id.id,)
            self._cr.execute(req, rub)
            res = self._cr.dictfetchall()
            if res:
                qtt = res[0].get('qty')
                self.qty_dispo = qtt
            else:
                self.qty_dispo = 0
            self.observation = ''
            self.onchange_qty()
            # self.state = 'error'
        else:
            if self.product_id:
                self.state = 'error'
                self.observation = 'Ce produit, n\'a pas d\'emplacement stock par défaut. Veuillez verifier cette information dans la catégorie du produit'

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            # if not self.description:
            #     self.description = self.product_id.name

            self.description = self.product_id.name

            if self.location_id:
                req = 'select sum(quantity) as qty from stock_quant where product_id=%s and location_id=%s;'
                rub = (self.product_id.id, self.location_id.id,)
                self._cr.execute(req, rub)
                res = self._cr.dictfetchall()
                if res:
                    qtt = res[0].get('qty')
                    self.qty_dispo = qtt
                else:
                    self.qty_dispo = 0
            else:
                self.state = 'error'
                # self.observation = 'Ce produit, n\'a pas d\'emplacement stock par défaut. Veuillez verifier cette information dans la catégorie du produit'

    @api.multi
    def action_valider(self):
        self.state = 'to_purchase'

    @api.multi
    def action_refuser(self):
        self.state = 'refus'

    @api.multi
    def action_disponible(self):
        if self.product_id:
            self.state = 'dispo'
        else:
            raise UserError(_('Veuillez sélectionner le produit en question avant de positionner la ligne sur DISPONIBLE'))

    @api.multi
    def action_a_acheter(self):
        if self.product_id:
            self.state = 'to_purchase'
        else:
            raise UserError(_(u'Veuillez soit sélectionner le produit s\'il existe dans le catalogue produit, sinon le créer dans le cas contraire'))


class DemandeAchatServiceLine(models.Model):
    _name = 'demande.achat.service.line'
    _description = 'ligne demande achat service'

    description = fields.Char('Description de la demande', required=True)
    qty         = fields.Float(u'Quantité demandée', default=1)
    product_id  = fields.Many2one('product.product', string='Produit', required=True)
    uom_id = fields.Many2one(related='product_id.uom_id', string=u'Unité', readonly=True)
    demande_id  = fields.Many2one('demande.achat', string='Demande')
    dem_global  = fields.Boolean(related='demande_id.dem_global', string='Demande globale')

    state       = fields.Selection([('new', 'Nouvelle'),
                                    ('waiting', 'En attente'),
                                    ('valid', u'Validée'),
                                    ('refus', u'Refusée'),
                                    ('to_purchase', 'A acheter'),
                                    ('done', u'Traitée'),
                                    ('cancel', u'Annulée')], default='new', string='Etat')
    observation = fields.Char('Observation')

    @api.multi
    def action_valider(self):
        self.state = 'to_purchase'

    @api.multi
    def action_refuser(self):
        self.state = 'refus'

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            if not self.description:
                self.description = self.product_id.name
            else:
                if self.dem_global:
                    self.description = self.product_id.name
