# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    type_stock = fields.Selection(related='location_id.usage', string='Type')
    category_id = fields.Many2one(related='product_id.categ_id', string=u'Catégorie', readonly=True)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    color = fields.Integer('Color Index')


class StockPrint(models.Model):
    _name = 'ra.stock.print'
    _description = 'Imprimer l etat de stock'

    name        = fields.Char('Titre', required=True, readonly=1, states={'draft': [('readonly', False)]})
    date        = fields.Datetime(u'Date génération', readonly=True)
    user_id     = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.uid, readonly=True)
    state       = fields.Selection([('draft', 'Nouveau'), ('done', u'Terminé')], string='Etat', default='draft')
    line_ids    = fields.One2many('ra.stock.print.line', 'stock_id', string='Lines')
    company_id  = fields.Many2one('res.company', string=u'Société', default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    observation = fields.Text('Observation')

    # parametres
    category_ids = fields.Many2many('product.category', string=u'Catégories')
    qty_dispo = fields.Boolean('Quantités disponibles seulement')
    location_type = fields.Selection([
        ('supplier', 'Vendor Location'),
        ('view', 'View'),
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('inventory', 'Inventory Loss'),
        ('procurement', 'Procurement'),
        ('production', 'Production'),
        ('transit', 'Transit Location')], string='Location Type',
        default='internal', index=True, required=True,
        help="* Vendor Location: Virtual location representing the source location for products coming from your vendors"
             "\n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products"
             "\n* Internal Location: Physical locations inside your own warehouses,"
             "\n* Customer Location: Virtual location representing the destination location for products sent to your customers"
             "\n* Inventory Loss: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)"
             "\n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (vendor or production) is not known yet. This location should be empty when the procurement scheduler has finished running."
             "\n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products"
             "\n* Transit Location: Counterpart location that should be used in inter-companies or inter-warehouses operations")

    # @api.one
    def action_generate_stock(self):
        lst = self.env['stock.quant'].search([('type_stock', '=', self.location_type),
                                              ('category_id', 'in', self.category_ids.ids)])
        i = 1
        self.date = fields.datetime.now()
        self.line_ids.unlink()
        for rec in lst:
            # print_v = True
            # if self.qty_dispo is True and rec.qty == 0.0:
            #     print_v = False

            # if print_v:
            if True:
                self.env['ra.stock.print.line'].create({
                    'name': i,
                    'stock_id': self.id,
                    'product_id': rec.product_id.id,
                    'qty': rec.qty,
                    'price': rec.inventory_value,
                    'in_date': rec.in_date,
                    'location_id': rec.location_id.id,
                })
                i += 1

    # @api.one
    def action_export_excel(self):

        w_file_name = self.name + '.xlsx'

        workbook = xlsxwriter.Workbook('tmp/'+w_file_name)
        worksheet = workbook.add_worksheet()

        # format
        money_mask         = '#,##0.00'
        titre_bold         = workbook.add_format({'bold': True, 'valign': 'vcenter', 'font_size': 28})
        bold               = workbook.add_format({'bold': True})
        bold_colonne       = workbook.add_format({'bg_color': '#C6C8CE', 'bold': True, 'border': 1})
        money              = workbook.add_format({'align': 'right', 'num_format': money_mask, 'border': 1})
        format_row = workbook.add_format({'align': 'left', 'font_size': 12, 'border': 1})

        worksheet.write('B2', self.company_id.name, bold)

        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 5)
        worksheet.set_column('C:C', 45)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 20)
        worksheet.set_column('F:F', 5)
        worksheet.set_column('G:G', 20)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 25)

        worksheet.write('D3', self.name, titre_bold)
        worksheet.write('D6', 'Genere le ' + self.date)
        worksheet.write('D7', 'Par ' + self.user_id.name)

        # titre des colonnes
        ligne_x = 8

        worksheet.write(ligne_x, 1, '#', bold_colonne)
        worksheet.write(ligne_x, 2, 'Produit', bold_colonne)
        worksheet.write(ligne_x, 3, 'Categorie', bold_colonne)
        worksheet.write(ligne_x, 4, 'Quantite', bold_colonne)
        worksheet.write(ligne_x, 5, 'U', bold_colonne)
        worksheet.write(ligne_x, 6, 'Valeur', bold_colonne)
        worksheet.write(ligne_x, 7, 'Emplacement', bold_colonne)
        worksheet.write(ligne_x, 8, 'Derniere modif.', bold_colonne)
        worksheet.write(ligne_x, 9, 'Note', bold_colonne)

        # valeur des lignes
        r = 1
        for row in self.line_ids:

            worksheet.write(ligne_x + r, 1, row.name, format_row)
            worksheet.write(ligne_x + r, 2, row.product_id.name, format_row)
            worksheet.write(ligne_x + r, 3, row.categ_id.name, format_row)
            worksheet.write(ligne_x + r, 4, row.qty, money)
            worksheet.write(ligne_x + r, 5, row.unite_id.name, format_row)
            worksheet.write(ligne_x + r, 6, row.price, money)
            worksheet.write(ligne_x + r, 7, row.location_id.name, format_row)
            worksheet.write(ligne_x + r, 8, row.in_date, format_row)
            if row.note:
                worksheet.write(ligne_x + r, 9, row.note, format_row)
            else:
                worksheet.write(ligne_x + r, 9, '', format_row)
            r += 1

        workbook.close()

        m = open('tmp/'+w_file_name, 'rb')
        self.env['ir.attachment'].create({
            'name'        : w_file_name,
            'datas'       : base64.b64encode(m.read()),
            'description' : 'files',
            'res_name'    : w_file_name,
            'res_model'   : 'ra.stock.print',
            'res_id'      : self.id,
            'datas_fname' : w_file_name,
            })

    # @api.multi
    def unlink(self):
        if self.state != 'draft':
            raise UserError(_(u'Suppression non autorisée ! \n\n  Le document est déjà validé !'))
        else:
            rec = super(StockPrint, self).unlink()
            return rec

    # @api.one
    def action_validate(self):
        self.state = 'done'

    # @api.one
    def action_draft(self):
        self.state = 'draft'


class StockPrintLine(models.Model):
    _name = 'ra.stock.print.line'
    _description = 'Lignes stock'
    _order = 'name'

    name        = fields.Integer('Numero', readonly=True)
    stock_id    = fields.Many2one('ra.stock.print', string='Stock', readonly=True)
    product_id  = fields.Many2one('product.product', string='Produit', required=True, readonly=True)
    categ_id    = fields.Many2one(related='product_id.categ_id', string=u'Catégorie', readonly=True)
    qty         = fields.Float('Quantité', readonly=True)
    unite_id    = fields.Many2one(related='product_id.uom_id', string=u'Unité de mesure', readonly=True)
    price       = fields.Float('Valeur', readonly=True)
    in_date     = fields.Datetime('Dernier mouvement', readonly=True)
    location_id = fields.Many2one('stock.location', string='Emplacement', readonly=True)
    note        = fields.Char('Note')
