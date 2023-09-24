from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id, )
    objectif_ids = fields.One2many('res.users.objectif', 'user_id')
    objectif = fields.Char()


class ResUsersObjectif(models.Model):
    _name = 'res.users.objectif'

    user_id = fields.Many2one('res.users')
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id, )
    objectif = fields.Monetary(string='Objectif Commercial', currency_field='currency_id')
    month = fields.Selection([
        ('01', 'Janvier'),
        ('02', 'Février'),
        ('03', 'Mars'),
        ('04', 'Avril'),
        ('05', 'Mai'),
        ('06', 'Juin'),
        ('07', 'Juilet'),
        ('08', 'Aout'),
        ('09', 'Septembre'),
        ('10', 'Octobre'),
        ('11', 'Novembre'),
        ('12', 'Décembre'),
    ], string='Mois', required=1)
    year = fields.Integer('Exercice', required=1)
