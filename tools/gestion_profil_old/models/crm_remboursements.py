from lxml import etree
from odoo import models, api


class CrmDesistement(models.Model):
    _inherit = "crm.desistement"

    @api.model
    def fields_view_get(self, view_id=None, view_type=None, toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        group_commercial = self.env['res.users'].has_group('gestion_profil.group_commercial')
        group_res_commercial = self.env['res.users'].has_group('gestion_profil.group_res_commercial')
        group_charg_recouvrement = self.env['res.users'].has_group('gestion_profil.group_charg_recouvrement')
        group_res_recouvrement = self.env['res.users'].has_group('gestion_profil.group_res_recouvrement')
        group_adv = self.env['res.users'].has_group('gestion_profil.group_adv')
        group_res_adv = self.env['res.users'].has_group('gestion_profil.group_res_adv')
        group_comptable_stock = self.env['res.users'].has_group('gestion_profil.group_comptable_stock')
        group_res_compta = self.env['res.users'].has_group('gestion_profil.group_res_compta')

        doc = etree.XML(res['arch'])
        # input 1 edit 0
        if group_commercial or group_res_commercial or group_adv:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '1')
                node.set('edit', '1')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '1')
                node.set('edit', '1')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)

        # input 0 edit 0
        if group_charg_recouvrement or group_res_recouvrement or group_res_adv or group_comptable_stock or group_res_compta:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)

        return res


class CrmRemboursement(models.Model):
    _inherit = "crm.remboursement"

    @api.model
    def fields_view_get(self, view_id=None, view_type=None, toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        group_commercial = self.env['res.users'].has_group('gestion_profil.group_commercial')
        group_res_commercial = self.env['res.users'].has_group('gestion_profil.group_res_commercial')
        group_charg_recouvrement = self.env['res.users'].has_group('gestion_profil.group_charg_recouvrement')
        group_res_recouvrement = self.env['res.users'].has_group('gestion_profil.group_res_recouvrement')
        group_adv = self.env['res.users'].has_group('gestion_profil.group_adv')
        group_res_adv = self.env['res.users'].has_group('gestion_profil.group_res_adv')
        group_comptable_stock = self.env['res.users'].has_group('gestion_profil.group_comptable_stock')
        group_res_compta = self.env['res.users'].has_group('gestion_profil.group_res_compta')

        doc = etree.XML(res['arch'])
        # input 1 edit 0
        if group_commercial or group_res_commercial or group_adv:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '1')
                node.set('edit', '1')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '1')
                node.set('edit', '1')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)

        # input 0 edit 0
        if group_charg_recouvrement or group_res_recouvrement or group_res_adv or group_comptable_stock or group_res_compta:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)

        return res
