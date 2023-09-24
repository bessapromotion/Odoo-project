# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from . import article


class Avenant(models.Model):
    """
    Avenant
    """
    _name        = 'hr.contract.avenant'
    _description = 'Avenant contrat'

    name         = fields.Char(u'Référence', required=True, readonly=1, default='/', states={'draft': [('readonly', False)]})
    user_id      = fields.Many2one('res.users', string='Etabli par', default=lambda self: self.env.user, readonly=1)

    contract_id        = fields.Many2one('hr.contract', string='Contrat', required=True)
    employee_id        = fields.Many2one(related='contract_id.employee_id', string=u'Employé')
    date_etablissement = fields.Date("Date d'établissement", default=fields.Date.today(), required=True)
    date_application   = fields.Date("Date d'application", default=fields.Date.today(), required=True)

    article_ids  = fields.One2many('hr.contract.avenant.article', 'avenant_id')

    state        = fields.Selection([
        ('draft',  'Nouveau'),
        ('open',   'En cours'),
        ('close',  u'Expiré'),
        ('cancel', u'Annulé')
    ], string='Statut', help="Statut de l'avenant", default='draft')


    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            pre = 'AVN'
            suf = 'DRH'
            num = self.env['ir.sequence'].get('hr.contract.avenant') or '/'
            vals['name'] = pre + '/' + num + '/' + suf + '/' + str(vals.get('date_etablissement')[:4])

        return super(models.Model, self).create(vals)

    def action_print(self):
        return self.env.ref('r_contract.act_report_avenant').report_action(self)


    # [[TODO]]
    # REMOVE THIS METHOD, FOR TEST PURPOSES <<<<<========
    @api.onchange('article_ids')
    def _print_articles(self):
        print('DEBUG: Avenant articles', self.article_ids)

class ArticleAvenant(models.Model):
    """
    Article d'un avenant
    """
    _name        = 'hr.contract.avenant.article'
    _description = 'Article dans un avenant'

    name         = fields.Char('Nom', required=True)
    contenu      = fields.Html(string='Contenu', default='', strip_style=True, strip_classes=True, required=True)

    avenant_id   = fields.Many2one('hr.contract.avenant', string='Avenant', required=True)

    modele_article_id = fields.Many2one('hr.contract.avenant.article.modele', string='Modéle', store=False)


    @api.onchange('modele_article_id')
    def _onchange_modele(self):
        if self.modele_article_id.id is not False:
            variables      = self.avenant_id.contract_id.get_variables()
            # print('DEBUG: variables', variables)
            # print('DEBUG: modele_contenu', self.modele_article_id.contenu)
            processed_text = article.Article.replace_keywords(self.modele_article_id.contenu, variables)
            # print('DEBUG: processed_text', processed_text)

            self.contenu   = processed_text



class ModeleArticleAvenant(models.Model):
    """
    Modele d'article d'un avenant
    """
    _name        = 'hr.contract.avenant.article.modele'
    _description = "Modele d'un Article dans un avenant"

    name         = fields.Char('Nom', required=True)
    contenu      = fields.Html(string='Contenu', strip_style=True, strip_classes=True, required=True)


    # selection__hr_contract_avenant_article_modele__contract_field__trial
    contract_field = fields.Selection([
        ('wage',   'Salaire'),
        ('trial', u"Période d'essai"),
    ], string='Champ du contrat', help="Champ du contrat", default='', store=False)

    """
    wage             = fields.Monetary('Salaire', store=False)
    currency_id      = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True, store=False)
    company_id       = fields.Many2one('res.company', readonly=False, default=lambda self: self.env.company, required=True, store=False)

    type_salaire     = fields.Selection([('base', 'Salaire de base'),
                                         ('brut', 'Salaire brut'),
                                         ('net', 'Salaire net'), ], string='Type salaire', store=False)
    trial_date_start = fields.Date("Date début période d'essai", store=False)
    trial_date_end   = fields.Date("Date fin période d'essai", store=False)

    old_vals = fields.Text('Old vals', store=False)
    new_vals = fields.Text('New vals', store=False)
    """

