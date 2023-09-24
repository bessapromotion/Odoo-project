# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class CreateDocumentWizard(models.TransientModel):
    _name = 'purchase.create.document.wizard'
    _description = 'creation des documents de la demande'

    demande_id = fields.Many2one('demande.achat', string='Demande achat', readonly=True)
    destination = fields.Selection([('demandeur', 'Livrer au demandeur'),
                                    ('stock', u'Entrée en stock'),
                                    ('entrepot', u'Transfert vers un dépôt')], string='Destination',
                                   help=u'Quelle est la destination des produits demandé')
    stock_destination_id = fields.Many2one('stock.location', string='Stock destination')
    methode = fields.Selection(
        [('consultation', 'Consulter plusieurs fournisseurs'), ('fournisseur', 'Consulter un fournisseur particulier')],
        string=u'Méthode de consultation', default='consultation')
    methode_req = fields.Selection(
        [('new', 'Nouvelle consultation'), ('old', 'Ajouter a une consultation en cours de préparation')],
        default='new', string='Nature de la consutation')
    partner_id = fields.Many2one('res.partner', string='Fournisseur')
    requition_id = fields.Many2one('purchase.requisition', string='Consultation')
    achat = fields.Boolean('Achat')
    affect = fields.Boolean('Affect')
    type_demande = fields.Selection([('achat', 'Achat'), ('service', 'Service')], string='Type demande')

    def action_create_ao(self, requisition_id=None):
        # Créer le convention
        if not requisition_id:
            consult = self.env['purchase.requisition'].create({
                'name': self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender'),
                'user_id': self.demande_id.responsable_id.id,
                'type_id': 2,
                'demande_id': self.demande_id.id,
                'schedule_date': self.demande_id.date_prevue,
                'state': 'in_progress',
                'origin': self.demande_id.name,
                'company_id': self.demande_id.company_id.id,
            })
            requisition_id = consult

        if self.demande_id.type_demande == 'achat':
            for rc in self.demande_id.line_ids:
                if rc.qty_achat > 0 and rc.state == 'to_purchase':
                    self.env['purchase.requisition.line'].create({
                        # 'name'       : str(nbr_line+1),
                        'product_id': rc.product_id.id,
                        'product_qty': rc.qty_achat,
                        'product_uom_id': rc.product_id.uom_id.id,
                        # 'des/cription': rc.product_id.name,
                        'requisition_id': requisition_id.id,
                        'schedule_date': self.demande_id.date_prevue,
                    })
        else:
            for rc in self.demande_id.line_service_ids:
                if rc.qty > 0 and rc.state == 'to_purchase':
                    self.env['purchase.requisition.line'].create({
                        # 'name'       : str(nbr_line+1),
                        'product_id': rc.product_id.id,
                        'product_qty': rc.qty,
                        'product_uom_id': rc.product_id.uom_id.id,
                        # 'des/cription': rc.product_id.name,
                        'requisition_id': requisition_id.id,
                        'schedule_date': self.demande_id.date_prevue,
                    })
        return requisition_id.id

    def get_type_operation(self, location):
        type_move = self.env['stock.picking.type'].search(
            [('default_location_src_id', '=', location), ('mise_a_dispo', '=', 'mad'), ])
        # type_move = self.env['stock.picking.type'].search([('default_location_src_id', '=', location), ('code', '=', 'internal') ])
        if type_move.exists():
            return type_move[0]
        else:
            return None

    def get_picking_id(self, type_operation):
        picking = self.env['stock.picking'].search(
            [('picking_type_id', '=', type_operation.id), ('demande_id', '=', self.demande_id.id), ])
        if picking.exists():
            return picking[0].id
        else:
            # res_model, loc_id = self.env['ir.model.data'].get_object_reference('demande_achat', 'location_mad')
            loc_id = self.env['stock.location'].search(
                [('usage', '=', 'customer'), ('name', '=', 'Mise a disposition')])

            picking = self.env['stock.picking'].create({
                'user_id': self.demande_id.user_id.id,
                'employe_id': self.demande_id.employe_id.id,
                'department_id': self.demande_id.department_id.id,
                'project_id': self.demande_id.project_id.id or None,
                'demande_id': self.demande_id.id,
                'state': 'draft',
                'origin': self.demande_id.name,
                'picking_type_id': type_operation.id,
                'move_type': 'direct',
                'company_id': self.demande_id.company_id.id,
                'create_uid': self.demande_id.user_id.id,
                'create_date': datetime.now(),
                'write_uid': self.demande_id.user_id.id,
                'write_date': datetime.now(),
                # 'min_date': datetime.now(),
                # 'max_date': datetime.now(),
                'printed': False,
                'location_dest_id': loc_id[0].id,
                'location_id': type_operation.default_location_src_id.id,
            })
            return picking[0].id

    def action_create_doc_affectation2(self):
        for rc in self.demande_id.line_ids:
            if (rc.qty_dispo > 0 or rc.qty_achat > 0) and rc.state in ('to_purchase', 'dispo'):
                # res_model, loc_id = self.env['ir.model.data'].get_object_reference('demande_achat', 'location_mad')
                loc_id = self.env['stock.location'].search(
                    [('usage', '=', 'customer'), ('name', '=', 'Mise a disposition')])
                type_operation = self.get_type_operation(rc.location_id.id)
                if type_operation:
                    picking = self.get_picking_id(type_operation)
                    self.env['stock.move'].create({
                        'product_id': rc.product_id.id,
                        'name': rc.product_id.name,
                        'origin': self.demande_id.name,
                        'create_uid': self.demande_id.user_id.id,
                        'create_date': datetime.now(),
                        'write_uid': self.demande_id.user_id.id,
                        'write_date': datetime.now(),
                        'product_uom': rc.product_id.product_tmpl_id.uom_id.id,
                        'product_uom_qty': rc.qty,
                        'procure_method': 'make_to_stock',
                        'picking_type_id': type_operation.id,
                        'location_id': type_operation.default_location_src_id.id,
                        'sequence': 10,
                        'company_id': self.demande_id.company_id.id,
                        'state': 'draft',
                        # 'ordred_qty': rc.qty,
                        # 'date_expected': datetime.now(),
                        # 'partially_available': False,
                        # 'propagate': True,
                        'location_dest_id': loc_id[0].id,
                        'date': datetime.now(),
                        'scrapped': False,
                        'picking_id': picking,
                    })
                else:
                    raise UserError(_(
                        u'Aucun mouvement Transfert interne n\'est créé. veuillez le créer en positionnant le champs (Opération interne) a Mise a disposition'))

    def action_create_doc_transfert(self):
        for rc in self.demande_id.line_ids:
            if (rc.qty_dispo > 0 or rc.qty_achat > 0) and rc.state in ('to_purchase', 'dispo'):
                type_operation = self.get_type_operation(rc.location_id.id)
                if type_operation:
                    picking = self.get_picking_id(type_operation)
                    self.env['stock.move'].create({
                        'product_id': rc.product_id.id,
                        'name': rc.product_id.name,
                        'origin': self.demande_id.name,
                        'create_uid': self.demande_id.user_id.id,
                        'create_date': datetime.now(),
                        'write_uid': self.demande_id.user_id.id,
                        'write_date': datetime.now(),
                        'product_uom': rc.product_id.product_tmpl_id.uom_id.id,
                        'product_uom_qty': rc.qty,
                        'procure_method': 'make_to_stock',
                        'picking_type_id': type_operation.id,
                        'location_id': type_operation.default_location_src_id.id,
                        'sequence': 10,
                        'company_id': self.demande_id.company_id.id,
                        'state': 'draft',
                        'location_dest_id': self.stock_destination_id.id,
                        'date': datetime.now(),
                        'scrapped': False,
                        'picking_id': picking,
                    })
                else:
                    raise UserError(_(
                        u'Aucun mouvement Transfert interne n\'est créé. veuillez le créer en positionnant le champs (Opération interne) a Mise a disposition'))

    def action_create_po(self, requisition=None):
        # Créer le convention
        po = self.env['purchase.order'].create({
            'user_id': self.demande_id.responsable_id.id,
            'partner_id': self.partner_id.id,
            'project_id': self.demande_id.project_id.id or None,
            'origin': self.demande_id.name,
            'requisition_id': requisition,
            'company_id': self.demande_id.company_id.id,
        })
        po.onchange_partner_id()

        if self.demande_id.type_demande == 'achat':
            for rc in self.demande_id.line_ids:
                if rc.qty_achat > 0 and rc.state == 'to_purchase':
                    prod_line = self.env['purchase.order.line'].create({
                        'name': rc.product_id.name,
                        'product_id': rc.product_id.id,
                        'product_qty': rc.qty_achat,
                        'product_uom': rc.product_id.uom_id.id,
                        # 'des/cription': rc.product_id.name,
                        'order_id': po.id,
                        'price_unit': 0.0,
                        'date_planned': self.demande_id.date_prevue or datetime.now(),
                    })
                    prod_line.onchange_product_id()
                    prod_line.product_qty = rc.qty_achat
        else:
            for rc in self.demande_id.line_service_ids:
                if rc.qty > 0 and rc.state == 'to_purchase':
                    prod_line = self.env['purchase.order.line'].create({
                        'name': rc.product_id.name,
                        'product_id': rc.product_id.id,
                        'product_qty': rc.qty,
                        'product_uom': rc.product_id.uom_id.id,
                        # 'des/cription': rc.product_id.name,
                        'order_id': po.id,
                        'price_unit': 0.0,
                        'date_planned': self.demande_id.date_prevue or datetime.now(),
                    })
                    prod_line.onchange_product_id()
                    prod_line.product_qty = rc.qty
        return po.id

    def action_appliquer(self):
        self.demande_id.state = 'done'
        if self.affect:
            if self.destination == 'demandeur':
                self.action_create_doc_affectation2()
            else:
                self.action_create_doc_transfert()

        if self.achat:
            if self.methode == 'consultation':
                self.demande_id.has_requisition = True
                if self.methode_req == 'new':
                    self.action_create_ao()
                else:
                    self.action_create_ao(self.requition_id)
            else:  # fournisseur
                po = self.action_create_po()
                return {
                    'type': 'ir.actions.act_window',
                    'name': 'Demande de prix',
                    'target': 'current',  # use 'current/new' for not opening in a dialog
                    'res_model': 'purchase.order',
                    'res_id': po,
                    'view_type': 'form',
                    'view_mode': 'form',
                }
