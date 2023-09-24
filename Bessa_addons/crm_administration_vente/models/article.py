# -*- coding: utf-8 -*-

from odoo import models, fields, api

import re


class Article(models.Model):
    """
    Article definition
    """
    _name = 'cahier.charge.article'
    _description = 'Article Cahier de charge'
    # _check_company_auto = True

    name = fields.Char('Nom', required=True)
    code = fields.Char('Code', required=False, copy=False)
    # en_cours = fields.Boolean(string=u'Dernière version', default=True, readonly=True)
    #
    # date_debut_application = fields.Date(u"Date de début d'application", default=fields.Date.today())
    # date_fin_application = fields.Date("Date de fin d'application")

    contenu = fields.Html(string='Contenu', strip_style=True, strip_classes=True, required=True)

    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)
    manager = fields.Char(string='Manager')
    _sql_constraints = [
        ('code_unique', 'unique(code)', "Le code d'article existe déjà.")
    ]

    # Things to add
    # - "Add a revision" button => duplicated the current Article and set the parent
    #    on validation, make the parent.en_cours=False and change the date_fin_application=today
    #    and replace the parent in the contract type with the revision id

    # @api.constrains('date_debut_application', 'date_fin_application')
    # def _check_dates(self):
    #     if self.date_fin_application is not False and self.date_fin_application <= self.date_debut_application:
    #         raise ValidationError("La date de fin d'application ne peut pas être avent celle du début d'application.")

    @api.model
    def create(self, vals):
        article_revision = super(Article, self).create(vals)

        # if article_revision.parent is not False:
        #     # Process the revision
        #     article_revision.parent.en_cours = False
        #     # article_revision.date_fin_application = fields.Date.today()
        #     self.update_contract_models('create', article_revision)
        return article_revision

    # Maybe remove the 'delete' permission
    """
    def unlink(self):
        print('DEBUG: Deleting record')
        if self.parent is not False:
            self.parent.en_cours = True
        self.update_contract_models('unlink', self)

        return super().unlink()
    """

    def set_values(self):
        if self.company_id.id == 1:
            self.manager = 'Amazigh Redouane BESSA.'
        if self.company_id.id == 2:
            self.manager = self.company_id.contract_represente
        variables = {
            'manager': self.manager or '',
            'company': self.company_id.name or '',

            # TO ADD ALL THE NEEDED VARIABLES HERE
            # ...
        }
        """
        Replaces the placholders in the article text with their values

        :param variables: a dictionary with the placeholder name as a key and what it should be replaced with as the value
        :return:          html string
        """
        return Article.replace_keywords(self.contenu, variables)

    @staticmethod
    def replace_keywords(text, variables):
        """
        Replaces keywords in a text with their values
        """
        processed_text = text
        for (placeholder, value) in variables.items():
            processed_text = re.sub(re.escape('[[' + placeholder + ']]'), '<strong>' + str(value) + '</strong>',
                                    processed_text, flags=re.IGNORECASE)

        return processed_text

    @api.onchange('contenu')
    def _onchange_contenu(self):
        if self.contenu is not False:
            Article.set_values(self)
