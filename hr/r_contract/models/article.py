# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import re


class Article(models.Model):
    """
    Article definition
    """
    _name = 'hr.contract.article'
    _description = 'Article contrat'
    _check_company_auto = True

    name = fields.Char('Nom', required=True)
    code = fields.Char('Code', required=False, copy=False)
    parent = fields.Many2one('hr.contract.article', string='Article parent', readonly=True)
    en_cours = fields.Boolean(string=u'Dernière version', default=True, readonly=True)

    date_debut_application = fields.Date(u"Date de début d'application", default=fields.Date.today())
    date_fin_application = fields.Date("Date de fin d'application")

    contenu = fields.Html(string='Contenu', strip_style=True, strip_classes=True, required=True)

    company_id = fields.Many2one('res.company', string=u'Société', index=True, default=lambda self: self.env.company)

    _sql_constraints = [
        ('code_unique', 'unique(code)', "Le code d'article existe déjà.")
    ]

    # Things to add
    # - "Add a revision" button => duplicated the current Article and set the parent
    #    on validation, make the parent.en_cours=False and change the date_fin_application=today
    #    and replace the parent in the contract type with the revision id

    @api.constrains('date_debut_application', 'date_fin_application')
    def _check_dates(self):
        if self.date_fin_application is not False and self.date_fin_application <= self.date_debut_application:
            raise ValidationError("La date de fin d'application ne peut pas être avent celle du début d'application.")

    @api.model
    def create(self, vals):
        article_revision = super().create(vals)

        if article_revision.parent is not False:
            # Process the revision
            article_revision.parent.en_cours = False
            # article_revision.date_fin_application = fields.Date.today()
            self.update_contract_models('create', article_revision)

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

    def update_contract_models(self, event, article):
        """
        Update the article record in the contract models
        param event:   Can be one of: create, unlink, ... [[ TO UPDATE LIST ]]
        param article: Article object
        """
        if event == 'create':
            # Change the article record in the contract models by the latest revision
            recs = self.env['hr.contract.modele.article.line'].search([('article_id', '=', article.parent.id)])
            for r in recs:
                r.article_id = article.id
        elif event == 'unlink':
            # [[TODO]]
            # recs = self.env['hr.contract.modele.article.line'].search([('article_id', '=', article.id)])
            # if article.parent is not False:
            #     print('DEBUG: Article has parent')
            #     for r in recs:
            #         r.article_id = article.parent.id
            # else:
            # This doesn't completely remove the records, just nulls the article_id
            #     print("DEBUG: Article doesn't have parent")
            #     # for r in recs:
            #     #     r.unlink()
            #     recs.unlink()
            pass

    def action_new_revision(self):
        """
        Creates a new article revision for the current one
        """
        # Get the new version number
        rec = self.env['hr.contract.article'].search([('id', '=', self.parent.id)])
        version = 2
        while rec:
            version += 1
            rec = self.env['hr.contract.article'].search([('id', '=', rec.parent.id)])

        if version == 2:
            new_code = self.code + '_V2'
        else:
            new_code = re.sub(re.escape('_V') + '\d$', '_V' + str(version), self.code, flags=re.IGNORECASE)
            if new_code == self.code:
                new_code = self.code + '_V' + str(version)

        return {
            'name': _(u"Révision d'article"),
            'res_model': 'hr.contract.article',
            'type': 'ir.actions.act_window',
            'context': {
                'default_name': self.name,
                'default_code': new_code,
                'default_parent': self.id,
                'default_contenu': self.contenu,
            },
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('r_contract.article_form_view').id,
            'target': 'current'  # new
        }

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


class ContractModelArticleLine(models.Model):
    """
    Article Line definition in Contract Model
    List of moveable articles in a Contract Model
    """
    _name = 'hr.contract.modele.article.line'
    _description = "Ligne d'article dans un modele de contrat"
    _order = 'sequence'

    name = fields.Char(related='article_id.name', string='Nom')
    article_id = fields.Many2one('hr.contract.article', string='Article', domain=[('en_cours', '=', True)],
                                 change_default=True)
    code = fields.Char(related='article_id.code', string='Code', store=False)
    sequence = fields.Integer(string='Sequence', default=10)

    modele_id = fields.Many2one('hr.contract.modele', string=u'Modèle de contrat')


class ContractArticleLine(models.Model):
    """
    ArticleLine definition
    List of moveable articles in an employee Contract
    """
    _name = 'hr.contract.article.line'
    _description = "Ligne d'article dans un contrat"
    _order = 'sequence'

    name = fields.Char(related='article_id.name', string='Nom')
    article_id = fields.Many2one('hr.contract.article', string='Article', domain=[('en_cours', '=', True)],
                                 change_default=True)
    code = fields.Char(related='article_id.code', string='Code', store=False)
    sequence = fields.Integer(string='Sequence', default=10)

    contract_id = fields.Many2one('hr.contract', string='Contrat')
