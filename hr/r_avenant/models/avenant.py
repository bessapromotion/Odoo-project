# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class Contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    @api.depends('article_ids')
    def _list_articles(self):
        for rec in self:
            ln = len(rec.article_ids)
            if ln == 1:
                rec.article_list = 'l\'article ' + rec.article_ids[0].article
            elif ln == 2:
                rec.article_list = 'les articles ' + rec.article_ids[0].article + ' et ' + rec.article_ids[1].article
            elif ln == 3:
                rec.article_list = 'les articles ' + rec.article_ids[0].article + ', ' + rec.article_ids[
                    1].article + ' et ' + rec.article_ids[2].article
            elif ln == 4:
                rec.article_list = 'les articles ' + rec.article_ids[0].article + ', ' + rec.article_ids[
                    1].article + ', ' + rec.article_ids[2].article + ' et ' + rec.article_ids[3].article

    type_avenant = fields.Selection([('Contrat', 'Contrat'), ('Avenant', 'Avenant')], string='Type document',
                                    default='Contrat', required=True)
    parent_id = fields.Many2one('hr.contract', string='Contrat initial')
    avenant_ids = fields.One2many('hr.contract', 'parent_id', string='Avenants')
    article_ids = fields.One2many('hr.contract.avenant.line', 'contract_id', string='Articles')
    mois_appli = fields.Char('Mois prise application')
    article_list = fields.Char(compute=_list_articles, string='Articles changés')
    article_av_lines = fields.One2many('hr.avenant.article.line', 'avenant_id', string='lignes articles')
    article_fonction_lines = fields.One2many('hr.avenant.article.line', 'avenant_id', string='lignes articles',
                                             domain=[('code', '=', 'fonction')])
    article_remmuneration_lines = fields.One2many('hr.avenant.article.line', 'avenant_id', string='lignes articles',
                                                  domain=[('code', '=', 'remmuniration')])
    article_prolongation_lines = fields.One2many('hr.avenant.article.line', 'avenant_id', string='lignes articles',
                                                 domain=[('code', '=', 'prolongagtion')])
    code_changement = fields.Char()

    def action_rnv_contract(self):
        return {
            'name': _('Création Renouvellement'),
            'view_mode': 'form',
            'res_model': 'rnv.contract.wizard',
            'view_id': self.env.ref('r_avenant.creer_rnv_wizard_form_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_employee_id': self.employee_id.id,
                'default_contract_id': self.id,
                'default_job_id': self.job_id.id,
                'default_wage': self.wage,
                'default_categorie': self.categorie,
                'default_section': self.section,
            },
            'target': 'new',
        }

    def charger_articles_avenant(self):
        self.article_av_lines.unlink()
        art = self.env['hr.report.modele'].search([('type_id', '=', 'hr.avenant')])
        if art.exists():
            for rec in art.article_lines:
                self.env['hr.avenant.article.line'].create({
                    'article_id': rec.id,
                    'sequence': rec.sequence,
                    'partie': rec.partie,
                    'avenant_id': self.id,
                })

    def get_variables_avenant(self):
        # Returns a dictionary of the variable name and its value
        # which will be used in processing articles
        current_state = {
            'civilité': self.employee_id.civilite_id.name or '',
            'affectation': self.employee_id.project_id.name or '',
            'employé': self.employee_id.name or '',
            'durée_periode_essai_mois': self.trial_nbr_mois or 0,
            'durée_periode_essai_jours': self.trial_nbr_jours or 0,
            'durée_periode_essai': '',
            'type_contrat': self.type_id.name or '',
            'société': self.company_id.name or '',
            'date_debut_contrat': self.date_start.strftime("%d/%m/%Y") if self.date_start else '',
            'date_fin_contrat': self.date_end.strftime("%d/%m/%Y") if self.date_end else '',
            'duree_contrat': self.duree_contrat or '',
            'nbr_mois': self.nbr_mois or '',
            'trial_nbr_mois': self.trial_nbr_mois or '',
            'salaire_base': Contract.format_wage(self.wage),
            'poste_travail': self.job_id.name or '',
            # 'durée_préavis':             str(self.job_id.preavis or 0) +' '+ self.job_id.uom_preavis,
            'durée_préavis': str(self.preavis or 0) + ' ' + self.uom_preavis,

            # TO ADD ALL THE NEEDED VARIABLES HERE
            # ...
        }

        return current_state

    def open_wizard(self):
        # articles
        articles = []
        if self.type_id.code == 'CDD':
            art = '01'
        else:
            art = '01'

        if self.date_end:
            d_end = ' au ' + str(self.date_end.strftime('%d-%m-%Y'))
        else:
            d_end = ''

        articles.append({
            'name': '01',
            'article': art,
            'type_changement': 'engagement',
            'old_val': 'du ' + str(self.date_start.strftime('%d-%m-%Y')) + d_end
        })

        if self.type_id.code == 'CDD':
            art = '04'
        else:
            art = '04'
        articles.append({
            'name': '02',
            'article': art,
            'type_changement': 'fonction',
            'old_val': self.job_id.name,
        })

        if self.type_id.code == 'CDD':
            art = '05'
        else:
            art = '04'
        articles.append({
            'name': '03',
            'article': art,
            'type_changement': 'affectation',
            'old_val': self.department_id.name,
        })

        if self.type_id.code == 'CDD':
            art = '08'
        else:
            art = '08'
        articles.append({
            'name': '03',  # orginal: 04
            'article': art,
            'type_changement': 'remuneration',
        })
        # rubrique
        rub = []
        for rec in self.rubrique_ids:
            rub.append({
                'name': rec.name,
            })
        return {
            'name': _('Création Avenant'),
            'view_mode': 'form',
            'res_model': 'create.avenant.wizard',
            'view_id': self.env.ref('r_avenant.creer_avenant_wizard_form_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_employee_id': self.employee_id.id,
                'default_contract_id': self.id,
                'default_categorie': self.categorie,
                'default_section': self.section,
                'default_article_ids': articles,
                'default_rubrique_ids': rub,
                'default_wage': self.wage,
            },
            'target': 'new',
        }

    def action_print(self):
        if self.type_avenant == 'Avenant':
            self.charger_articles_avenant()
            return self.env.ref('r_avenant.act_report_avenant_contrat').report_action(self)
        else:
            if self.type_id.code == 'CDD':
                return self.env.ref('r_contract.act_report_contrat_cdd').report_action(self)
            else:
                return self.env.ref('r_contract.act_report_contrat_cdi').report_action(self)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            suf = 'DRH'
            num = self.env['ir.sequence'].get('hr.contract') or '/'
            vals['name'] = self.env['ir.sequence'].get('hr.contract') or '/'
            if vals.get('type_avenant') == 'Contrat':
                vals['date_entree'] = vals['date_start']

        return super(Contract, self).create(vals)

    def action_signer(self):
        # ctr = self.env['hr.contract'].search([])
        # for rec in ctr:
        #     rec._fill_articles()
        #     rec.state = 'open'
        #     titre = 'Avenant'
        #     if rec.type_avenant == 'Contrat':
        #         titre = 'Contrat de travail'
        #
        #     self.env['hr.employee.historique'].create({
        #         'employe_id' : rec.employee_id.id,
        #         'document'   : titre,
        #         'numero'     : rec.name,
        #         'date_doc'   : rec.date_start,
        #         'date_prise_effet' : rec.date_end,
        #         'user_id'    : rec.user_id.id,
        #         # 'state' : self.state,
        #         'note'       : rec.type_id.name,
        #         'model_name' : 'hr.contract',
        #         'model_id'   : rec.id,
        #     })

        if not self.employee_id.barcode:
            self.employee_id.generate_random_barcode()

        self.state = 'open'
        titre = 'Avenant'
        if self.type_avenant == 'Contrat':
            titre = 'Contrat de travail'

        self.env['hr.employee.historique'].create({
            'employe_id': self.employee_id.id,
            'document': titre,
            'numero': self.name,
            'date_doc': self.date_start,
            'date_prise_effet': self.date_end,
            'user_id': self.user_id.id,
            # 'state' : self.state,
            'note': self.type_id.name,
            'model_name': 'hr.contract',
            'model_id': self.id,
            'num_embauche': self.employee_id.num_embauche,
        })
        # mise a jour fiche employé
        self.employee_id.job_id = self.job_id.id
        self.employee_id.department_id = self.department_id.id


class ContractAvenantLine(models.Model):
    _name = 'hr.contract.avenant.line'

    name = fields.Char('Artilce avenant', readonly=1)
    article = fields.Char(u'Numéro article modifié')
    type_changement = fields.Selection([('engagement', 'L\'engagement'),
                                        ('fonction', 'La fonction'),
                                        ('affectation', 'L\'affectation'),
                                        ('remuneration', u'La rémunération'), ], string='type changement', readonly=1)
    old_val = fields.Char('Contrat initial', readonly=1)
    revision_val = fields.Char('Révisé comme...', readonly=1)
    contract_id = fields.Many2one('hr.contract', string='Contrat')
    # code            = fields.Char()


class AvenantArticleLine(models.Model):
    """
    ArticleLine definition
    List of moveable articles in an employee Contract
    """
    _name = 'hr.avenant.article.line'
    _description = "Ligne d'article dans un avenant"
    _order = 'sequence'

    name = fields.Char(related='article_id.name', string='Nom')
    article_id = fields.Many2one('hr.report.modele.article', string='Article',
                                 change_default=True)
    code = fields.Char(related='article_id.code', string='Code', store=False)
    sequence = fields.Integer(string='Sequence', default=10)
    partie = fields.Selection([('1', 'Partie 1'), ('2', 'Partie 2'), ('3', 'Partie 3')], string='Partie', default='1')

    avenant_id = fields.Many2one('hr.contract', string='Avenant')
