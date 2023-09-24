# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import date


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    @api.depends('order_line')
    def get_typologie_bien(self):
        for rec in self:
            if rec.order_line:
                if rec.order_line[0].product_id.type_id.name:
                    rec.typologie_bien = rec.order_line[0].product_id.format_id.name

    typologie_bien = fields.Char(string="Typologie du bien", compute='get_typologie_bien', store=True)
    project_id = fields.Many2one('project.project', string='Projet', readonly=1,
                                 states={'draft': [('readonly', False)]}, required=1, tracking=True)
    project_name = fields.Char(related='project_id.name', store=True, string='Nom Projet')
    mode_achat = fields.Selection([('1', 'Auto'), ('2', 'Crédit'), ('3', 'Mixte'), ], string='Mode Achat', required=1, tracking=True, default=False)
    validity_date = fields.Date(required=1, tracking=True, default=date.today())
    num_dossier = fields.Char(u'N° Dossier', required=1, tracking=True)
    auxiliaire_cpt = fields.Char(u'Auxiliaire compta')
    charge_recouv_id = fields.Many2one('res.users', string=u'Recouvrement', required=1,
                                       default=lambda self: self.env.user, tracking=True)
    motif_annulation = fields.Selection([('Basculement', 'Basculement'),
                                         ('annulation', 'Annulation'),
                                         ('desistement', 'Désistement'),
                                         ('Prereservation', 'Annulation préréservation')], string='Motif annulation')
    discount_state = fields.Boolean('Remise', store=True, default=False,readonly=True)
    new_price_m2 =fields.Float(string='Prix m² avec remise', tracking=True,store=1, readonly=True)
    type =fields.Selection([('1', 'Remise sur le  Prix_m²'),
                             ('2', 'Remise sur le Prix_vente'),
                             ('3', 'Remise d\'un Montant')], string='Type de remise', readonly=True )
    
    @api.onchange('project_id')
    def change_project_name(self):
        self.project_name = self.project_id.name

    @api.onchange('num_dossier')
    def action_update(self):
        if self.num_dossier:
            rec = self.env['sale.order'].search(
                [('num_dossier', '=', self.num_dossier), ('project_id', '=', self.project_id.id),
                 ('name', '!=', self.name)])
            if rec.exists():
                raise UserError(_(
                    u'Ce numéro de dossier existe déjà dans le projet actuel, veuillez saisir un code différent'))

        else:
            for res in self.reservation_ids:
                res.num_dossier = self.num_dossier
        
    def action_appliquer_remise(self):
        #print('avant')
        if self.company_id != self.env.company:
            raise UserError(_(u'Veuillez sélectionner la société %s', self.company_id.name))
        #print('apres')
        view_id = self.env['ir.model.data']._xmlid_to_res_id('crm_custom_.view_calcul_remise_pourcentage_form')
        ID = self.id
        order_line_id = self.order_line[0]
        print(ID)
        print(order_line_id.id)
        return {
            'name': 'Assistant d\'application d\'une remise',
            'view_mode': 'form',
            'views': [(view_id, 'form'), ],
            'res_model': 'calcul.remise.pourcentage.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_name': order_line_id.id,
                        'default_order_id': ID
                        },
            'target': 'new',
        }
    
    def change_mode_achat(self):
        print('mode d\'achat')

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    superficie = fields.Float(related='product_id.superficie', tracking=True, store=True)
    num_lot = fields.Char(related='product_id.num_lot', tracking=True)
    prix_m2 = fields.Float(string='Prix m2', tracking=True)
    name = fields.Char(related='product_tmpl_id2.name', string='Description', required=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price',compute='compute_price3', readonly=1)
    
    @api.onchange('name')
    def compute_price2(self):
        for rec in self:
           rec.prix_m2 = rec.product_id.prix_m2
           rec.price_unit = rec.superficie * rec.prix_m2

    @api.onchange('prix_m2')
    def compute_price3(self):
        for rec in self:
            rec.price_unit = rec.superficie * rec.prix_m2

