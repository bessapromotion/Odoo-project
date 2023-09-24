# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import re


class Article(models.Model):
    """
    Article definition
    """
    _name = 'hr.frt.motif.article'
    _description = 'Article contrat'
    _check_company_auto = True

    name = fields.Char('Nom', required=True)
    code = fields.Char('Code', required=False, copy=False)
    parent = fields.Many2one('hr.frt.motif.article', string='Article parent', readonly=True)
    en_cours = fields.Boolean(string=u'Dernière version', default=True, readonly=True)

    date_debut_application = fields.Date(u"Date de début d'application", default=fields.Date.today())
    date_fin_application = fields.Date("Date de fin d'application")

    contenu = fields.Html(string='Contenu', strip_style=True, strip_classes=True, required=True)

    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_unique', 'unique(code)', "Le code d'article existe déjà.")
    ]

    def set_values(self, variables):
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
