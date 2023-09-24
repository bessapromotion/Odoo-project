from odoo import models, fields


class Hr(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    sanctions_count = fields.Integer(compute='compute_sanctions_count')

    def compute_sanctions_count(self):
        for record in self:
            count = self.env['hr.sanction'].search_count(
                [('employe_id', '=', self.id)])
            if count > 0:
                record.sanctions_count = count
            else:
                record.sanctions_count = 0
    #
    # def get_sanctions(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Dossier disciplinaire',
    #         'view_mode': 'tree',
    #         'res_model': 'hr.sanction',
    #         'domain': [('employe_id', '=', self.id)],
    #         'context': "{'create': False}"
    #     }
