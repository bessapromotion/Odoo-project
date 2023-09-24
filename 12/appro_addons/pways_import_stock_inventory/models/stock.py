# -*- coding: utf-8 -*-
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
import io
import tempfile
import binascii
import logging
_logger = logging.getLogger(__name__)

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')

# class StockInventory(models.Model):
#     _inherit = 'stock.inventory'

#     def action_start(self):
#         for inventory in self.filtered(lambda x: x.state not in ('done','cancel')):
#             vals = {'state': 'confirm', 'date': inventory.date or fields.Datetime.now()}
#             if (inventory.filter != 'partial') and not inventory.line_ids:
#                 vals.update({'line_ids': [(0, 0, line_values) for line_values in inventory._get_inventory_lines_values()]})
#             inventory.write(vals)
#         return True


class ImportStockInventory(models.TransientModel):
    _name = "import.stock.inventory"

    file = fields.Binary('File')
    inv_name = fields.Char('Inventory Name', required=True)
    location_id = fields.Many2one('stock.location', "Location", required=True)
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='xls')
    import_prod_option = fields.Selection([('barcode', 'Barcode'),('code', 'Code'),('name', 'Name')],string='Import Product By ',default='code')
    location_id_option = fields.Boolean(string="Allow to Import Location on inventory line from file")
    is_validate_inventory = fields.Boolean(string="Validate Inventory")
    date = fields.Datetime(string='Inventory Date', default=lambda self: fields.datetime.now() , required=True)

    @api.multi
    def import_xls(self):
        if self.import_option == 'xls':
            try:
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
                fp.write(binascii.a2b_base64(self.file))
                fp.seek(0)
                values = {}
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise exceptions.Warning(_("Invalid file ! "))
            
            dict_list = []
            keys = sheet.row_values(0)
            values = [sheet.row_values(i) for i in range(1, sheet.nrows)]
            for value in values:
                dict_list.append(dict(zip(keys, value)))

            inventory_obj = self.env['stock.inventory']
            for line in dict_list:
                product_id = self.env['product.product'].sudo().search([('default_code', '=', line.get('code'))])
                if not product_id:
                    raise exceptions.Warning(_("Produit [%s] n'existe pas !" % line.get('code')))

                uom_id = self.env['uom.uom'].sudo().search([('name', '=', line.get('unit'))])
                if not uom_id:
                    raise exceptions.Warning(_("Unité de mesure %s n'existe pas !" % line.get('unit')))

                if not inventory_obj:
                    inventory_obj = inventory_obj.create({'name': self.inv_name, 'filter':'partial', 'location_id':self.location_id.id, 'date': self.date})
                if inventory_obj:
                    self.env['stock.inventory.line'].sudo().create({
                        'product_id': product_id.id,
                        'location_id': self.location_id.id,
                        'product_qty': float(line.get('qty')),
                        'product_uom_id': product_id.product_tmpl_id.uom_id.id,
                        'inventory_id': inventory_obj.id,
                    })
