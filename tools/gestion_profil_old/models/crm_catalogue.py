from lxml import etree
from odoo import models, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def fields_view_get(self, view_id=None, view_type=None, toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        group_commercial = self.env['res.users'].has_group('gestion_profil.group_commercial')
        group_res_commercial = self.env['res.users'].has_group('gestion_profil.group_res_commercial')
        group_charg_recouvrement = self.env['res.users'].has_group('gestion_profil.group_charg_recouvrement')
        group_res_recouvrement = self.env['res.users'].has_group('gestion_profil.group_res_recouvrement')
        group_adv = self.env['res.users'].has_group('gestion_profil.group_adv')
        group_res_adv = self.env['res.users'].has_group('gestion_profil.group_res_adv')
        group_assistante_adv = self.env['res.users'].has_group('gestion_profil.group_assistante_adv')
        group_comptable_stock = self.env['res.users'].has_group('gestion_profil.group_comptable_stock')
        group_res_compta = self.env['res.users'].has_group('gestion_profil.group_res_compta')

        doc = etree.XML(res['arch'])
        # consu
        if group_commercial or group_adv or group_res_adv or group_res_recouvrement or group_charg_recouvrement or group_assistante_adv or group_comptable_stock or group_res_compta:

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

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)
        # edit
        if group_res_commercial:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '1')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '1')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '1')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)

        return res


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def fields_view_get(self, view_id=None, view_type=None, toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        group_receptionniste = self.env['res.users'].has_group('gestion_profil.group_receptionniste')
        group_commercial = self.env['res.users'].has_group('gestion_profil.group_commercial')
        group_res_commercial = self.env['res.users'].has_group('gestion_profil.group_res_commercial')
        group_charg_recouvrement = self.env['res.users'].has_group('gestion_profil.group_charg_recouvrement')
        group_res_recouvrement = self.env['res.users'].has_group('gestion_profil.group_res_recouvrement')
        group_adv = self.env['res.users'].has_group('gestion_profil.group_adv')
        group_res_adv = self.env['res.users'].has_group('gestion_profil.group_res_adv')
        group_comptable_stock = self.env['res.users'].has_group('gestion_profil.group_comptable_stock')
        group_res_compta = self.env['res.users'].has_group('gestion_profil.group_res_compta')
        group_assistante_adv = self.env['res.users'].has_group('gestion_profil.group_assistante_adv')

        doc = etree.XML(res['arch'])
        if group_res_commercial or group_commercial or group_charg_recouvrement or group_res_recouvrement or group_adv or group_res_adv:

            nodes_form = doc.xpath("//form")
            for node in nodes_form:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '1')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//tree")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '1')
                node.set('delete', '0')

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)
        if group_receptionniste:

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

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '1')
                node.set('edit', '1')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)
        if group_assistante_adv:

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

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '1')
                node.set('edit', '1')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)
        if group_comptable_stock or group_res_compta:

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

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)

        return res


class ProjectProject(models.Model):
    _inherit = "project.project"

    # @api.multi
    def write(self, vals):
        if self.env['res.users'].has_group('gestion_profil.group_res_adv') or self.env['res.users'].has_group(
                'gestion_profil.group_res_compta') or self.env['res.users'].has_group(
            'gestion_profil.group_comptable_stock') or self.env['res.users'].has_group(
            'gestion_profil.group_assistante_adv') or self.env['res.users'].has_group('gestion_profil.group_adv') or \
                self.env['res.users'].has_group('gestion_profil.group_res_recouvrement') or self.env[
            'res.users'].has_group('gestion_profil.group_charg_recouvrement') or self.env['res.users'].has_group(
            'gestion_profil.group_receptionniste') or self.env['res.users'].has_group(
            'gestion_profil.group_commercial') or self.env['res.users'].has_group(
            'gestion_profil.group_res_commercial'):
            raise UserError(_('Vous n\'avez pas le droit de modifier !'))
        return super(ProjectProject, self).write(vals)

    @api.model
    def fields_view_get(self, view_id=None, view_type=None, toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        group_receptionniste = self.env['res.users'].has_group('gestion_profil.group_receptionniste')
        group_commercial = self.env['res.users'].has_group('gestion_profil.group_commercial')
        group_res_commercial = self.env['res.users'].has_group('gestion_profil.group_res_commercial')
        group_charg_recouvrement = self.env['res.users'].has_group('gestion_profil.group_charg_recouvrement')
        group_res_recouvrement = self.env['res.users'].has_group('gestion_profil.group_res_recouvrement')
        group_adv = self.env['res.users'].has_group('gestion_profil.group_adv')
        group_res_adv = self.env['res.users'].has_group('gestion_profil.group_res_adv')
        group_assistante_adv = self.env['res.users'].has_group('gestion_profil.group_assistante_adv')
        group_comptable_stock = self.env['res.users'].has_group('gestion_profil.group_comptable_stock')
        group_res_compta = self.env['res.users'].has_group('gestion_profil.group_res_compta')

        doc = etree.XML(res['arch'])
        if group_res_commercial or group_commercial or group_charg_recouvrement or group_res_recouvrement or group_adv or group_res_adv or group_assistante_adv or group_comptable_stock or group_res_compta or group_receptionniste:

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

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)

        return res


class ProjectTask(models.Model):
    _inherit = "project.task"

    # @api.multi
    def write(self, vals):
        if self.env['res.users'].has_group('gestion_profil.group_res_adv') or self.env['res.users'].has_group(
                'gestion_profil.group_res_compta') or self.env['res.users'].has_group(
            'gestion_profil.group_comptable_stock') or self.env['res.users'].has_group(
            'gestion_profil.group_assistante_adv') or self.env['res.users'].has_group('gestion_profil.group_adv') or \
                self.env['res.users'].has_group('gestion_profil.group_res_recouvrement') or self.env[
            'res.users'].has_group('gestion_profil.group_charg_recouvrement') or self.env['res.users'].has_group(
            'gestion_profil.group_receptionniste') or self.env['res.users'].has_group(
            'gestion_profil.group_commercial') or self.env['res.users'].has_group(
            'gestion_profil.group_res_commercial'):
            raise UserError(_('Vous n\'avez pas le droit de modifier !'))
        return super(ProjectTask, self).write(vals)

    @api.model
    def fields_view_get(self, view_id=None, view_type=None, toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        group_receptionniste = self.env['res.users'].has_group('gestion_profil.group_receptionniste')
        group_commercial = self.env['res.users'].has_group('gestion_profil.group_commercial')
        group_res_commercial = self.env['res.users'].has_group('gestion_profil.group_res_commercial')
        group_charg_recouvrement = self.env['res.users'].has_group('gestion_profil.group_charg_recouvrement')
        group_res_recouvrement = self.env['res.users'].has_group('gestion_profil.group_res_recouvrement')
        group_adv = self.env['res.users'].has_group('gestion_profil.group_adv')
        group_res_adv = self.env['res.users'].has_group('gestion_profil.group_res_adv')
        group_assistante_adv = self.env['res.users'].has_group('gestion_profil.group_assistante_adv')
        group_comptable_stock = self.env['res.users'].has_group('gestion_profil.group_comptable_stock')
        group_res_compta = self.env['res.users'].has_group('gestion_profil.group_res_compta')

        doc = etree.XML(res['arch'])
        if group_res_commercial or group_commercial or group_charg_recouvrement or group_res_recouvrement or group_adv or group_res_adv or group_assistante_adv or group_comptable_stock or group_res_compta or group_receptionniste:

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

            nodes_tree = doc.xpath("//kanban")
            for node in nodes_tree:
                node.set('import', '0')
                node.set('create', '0')
                node.set('edit', '0')
                node.set('delete', '0')

            res['arch'] = etree.tostring(doc)

        return res
