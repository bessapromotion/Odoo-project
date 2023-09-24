# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import re


class ReportModele(models.Model):
    _name = 'hr.report.modele'
    _description = 'Modele rapport'
    _check_company_auto = True

    name = fields.Char(u'Modèle de contrat')
    # type_id = fields.Many2one('ir.model', string=u'Modèle', required=True)
    type_id = fields.Char(string=u'Modèle', required=True)

    article_lines = fields.One2many('hr.report.modele.article', 'modele_id', string='Articles', copy=True)

    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)


class Article(models.Model):
    """
    Article definition
    """
    _name = 'hr.report.modele.article'
    _description = 'Article'
    _check_company_auto = True

    name = fields.Char('Nom', required=True)
    code = fields.Char('Code', required=False, copy=False)
    sequence = fields.Integer(string='Sequence', default=10)
    partie = fields.Selection([('1', 'Partie 1'), ('2', 'Partie 2'), ('3', 'Partie 3')], string='Partie', default='1')
    contenu = fields.Html(string='Contenu', strip_style=True, strip_classes=True, required=True)
    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)
    modele_id = fields.Many2one('hr.report.modele', string=u'Modèle de contrat')

    parent = fields.Many2one('hr.contract.article', string='Article parent', readonly=True)
    en_cours = fields.Boolean(string=u'Dernière version', default=True, readonly=True)

    date_debut_application = fields.Date(u"Date de début d'application", default=fields.Date.today())
    date_fin_application = fields.Date("Date de fin d'application")

    # _sql_constraints = [
    #     ('code_unique', 'unique()', "Le code d'article existe déjà.")
    # ]

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
