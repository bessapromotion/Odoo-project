# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from datetime import date
from odoo.exceptions import UserError


class CreerAvenantWizard(models.TransientModel):
    _name = 'create.avenant.wizard'

    employee_id = fields.Many2one('hr.employee', string='Employé', readonly=1, check_company=True)
    contract_id = fields.Many2one('hr.contract', string='Contrat initial', readonly=1)
    date_etablissement = fields.Date(u'Date établissement', default=fields.Date.today())
    date_prise_effet = fields.Date('Date prise d\'effet', default=date.today())
    article_ids = fields.One2many('create.avenant.wizard.line', 'wiz_id', string='Articles')
    # new values
    job_id = fields.Many2one('hr.job', string='Fonction')
    department_id = fields.Many2one('hr.department', string='Structure')
    date_start = fields.Date('Date début')
    date_end = fields.Date('Date fin')
    prolongation_ok = fields.Boolean(u'Prolongation', default=False)
    remuneration_ok = fields.Boolean(u'Révision de la rémunération')
    fonction_ok = fields.Boolean(u'Changement de fonction', default=False)
    wage = fields.Float('Nouveau salaire')
    categorie = fields.Char(u'Catégorie')
    section = fields.Char('Section')

    rubrique_ids = fields.One2many('create.avenant.wizard.rubrique', 'wiz_id', string='Rubriques')

    @api.onchange('job_id')
    def onchange_job(self):
        for rec in self:
            for ln in rec.article_ids:
                if ln.type_changement == 'fonction':
                    if rec.job_id:
                        ln.revision_val = rec.job_id.name
                    else:
                        ln.revision_val = ''
        self.department_id = self.env['hr.job'].search([('name', '=', self.job_id.name)]).department_id.id

    @api.onchange('department_id')
    def onchange_department(self):
        for rec in self:
            for ln in rec.article_ids:
                if ln.type_changement == 'affectation':
                    if rec.department_id:
                        ln.revision_val = rec.department_id.name
                    else:
                        ln.revision_val = ''

    @api.onchange('date_start', 'date_end', 'remuneration_ok', 'fonction_ok', 'prolongation_ok')
    def onchange_date(self):
        for rec in self:
            for ln in rec.article_ids:
                if ln.type_changement == 'engagement':
                    if rec.date_start:
                        if rec.date_end:
                            if rec.remuneration_ok or rec.fonction_ok:
                                if rec.date_prise_effet < rec.date_start:
                                    ln.revision_val = 'du ' + str(
                                        rec.date_prise_effet.strftime('%d-%m-%Y')) + ' au ' + str(
                                        rec.date_end.strftime('%d-%m-%Y'))
                                else:
                                    ln.revision_val = 'du ' + str(rec.date_start.strftime('%d-%m-%Y')) + ' au ' + str(
                                        rec.date_end.strftime('%d-%m-%Y'))
                        else:
                            if rec.remuneration_ok or rec.fonction_ok:
                                if rec.date_prise_effet < rec.date_start:
                                    ln.revision_val = 'du ' + str(rec.date_prise_effet.strftime('%d-%m-%Y'))
                                else:
                                    ln.revision_val = 'du ' + str(rec.date_start.strftime('%d-%m-%Y'))
                    else:
                        ln.revision_val = ''

    def action_create(self):
        if self.prolongation_ok:
            if self.date_start and self.date_end:
                if self.contract_id.type_id_code == 'CDD':
                    if self.contract_id.date_end is False:
                        raise UserError(_(u'Veuillez vérifier la date de fin du contrat!'))
                    else:
                        delta = self.date_start - self.contract_id.date_end
                        if delta != datetime.timedelta(days=1):
                            raise UserError(_(u'Veuillez vérifier la date de début de la prolongation!' + str(delta)))
                else:
                    raise UserError(_(u'Pas de prolongation pour un contrat à durée indéterminée!'))
            else:
                raise UserError(_(u'Veuillez saisir la date de début et la date de fin de la prolongation!'))
        else:
            # if self.date_prise_effet > self.contract_id.date_end or self.date_prise_effet < self.contract_id.date_start:
            if self.contract_id.date_start is False:
                raise UserError(_(u'Veuillez vérifier la date de début du contrat'))

            elif self.contract_id.type_id_code == 'CDD' and self.contract_id.date_end is False:
                raise UserError(_(u'Veuillez vérifier la date de fin du contrat'))

            # [[TODO]] edit to check the trial period instead of the contract period <<<<<======
            elif self.date_prise_effet < self.contract_id.date_start:
                raise UserError(_(u"La date de prise d'effet doit être postérieure à la date de début du contrat."))
            elif (self.contract_id.type_id_code == 'CDD' and self.date_prise_effet > self.contract_id.date_end):
                raise UserError(_(u"La date de prise d'effet doit être antérieure à la date d'expiration du contrat."))

        # mois prise effect
        mois = str(self.date_prise_effet)[5:7]
        annee = str(self.date_prise_effet)[:4]
        mois_liste = ['de janvier ', u'de fèvrier ', 'de mars ', 'd\'avril ', 'de mai ', 'de juin ',
                      'de juillet ', 'd\'aout ', 'de septembre ', 'd\'octobre ', 'de novembre ', u'de décembre ']
        val_mois = mois_liste[int(mois) - 1] + annee

        # engagement
        if self.date_start:
            date_d = self.date_start
            if self.date_end:
                date_e = self.date_end
            else:
                date_e = None
        else:
            date_d = self.contract_id.date_start
            date_e = self.contract_id.date_end

        # affectation
        if self.department_id:
            department = self.department_id.id
        else:
            department = self.contract_id.department_id.id
        # fonction
        if self.job_id:
            job = self.job_id.id
        else:
            job = self.contract_id.job_id.id

        # nbr mois
        nbr_mois = 0
        if self.date_start and self.date_end:
            delta = self.date_end - self.date_start
            nbr_mois = round((delta.days + 1) / 30)

        # get oldest date between date_start and date_prise_effet
        if self.fonction_ok or self.remuneration_ok:
            if self.date_start and self.date_prise_effet:
                if self.date_prise_effet < self.date_start:
                    date_d = self.date_prise_effet

        contrat = self.env['hr.contract'].create({
            'employee_id': self.employee_id.id,
            'num_embauche': self.contract_id.num_embauche,
            'parent_id': self.contract_id.id,
            'department_id': department,
            'date_entree': self.contract_id.date_entree,
            'user_id': self.env.user.id,
            'date_etablissement': self.date_etablissement,
            'type_avenant': 'Avenant',
            'type_id': self.contract_id.type_id.id,
            'job_id': job,
            'date_start': date_d,
            'date_end': date_e,
            'categorie': self.categorie,
            'hr_responsible_id': self.contract_id.hr_responsible_id.id,
            'section': self.section,
            'nbr_mois': nbr_mois,
            'mois_appli': val_mois,
            'wage': self.contract_id.wage,
            'preavis': self.contract_id.preavis,
            'type_salaire': self.contract_id.type_salaire,

            # NEW EDITS
            'modele_id': self.contract_id.modele_id.id,
            # 'trial_date_start': self.contract_id.trial_date_start,
            # 'trial_date_end': self.contract_id.trial_date_end,
            'trial_nbr_mois': self.contract_id.trial_nbr_mois,
            'structure_type_id': self.contract_id.structure_type_id.id if self.contract_id.structure_type_id else False,
            # 'struct_id': self.contract_id.struct_id.id if self.contract_id.struct_id else False,
        })
        if self.prolongation_ok:
            contrat.code_changement = 'prolongagtion'
        if self.fonction_ok:
            contrat.code_changement = 'fonction'
        if self.remuneration_ok:
            contrat.code_changement = 'remuneration'

        # artiles
        contrat.article_ids.unlink()
        # engagement
        i = 1
        if self.date_start:
            self.env['hr.contract.avenant.line'].create({
                'name': '01',
                'article': self.article_ids[0].article,
                'type_changement': self.article_ids[0].type_changement,
                'old_val': self.article_ids[0].old_val,
                'revision_val': self.article_ids[0].revision_val,
                'contract_id': contrat.id,
            })
            i += 1
        # fonction
        if self.job_id:
            self.env['hr.contract.avenant.line'].create({
                'name': '0' + str(i),
                'article': self.article_ids[1].article,
                'type_changement': self.article_ids[1].type_changement,
                'old_val': self.article_ids[1].old_val,
                'revision_val': self.article_ids[1].revision_val,
                'contract_id': contrat.id,
            })
            i += 1
        # department
        if self.department_id:
            self.env['hr.contract.avenant.line'].create({
                'name': '0' + str(i),
                'article': self.article_ids[2].article,
                'type_changement': self.article_ids[2].type_changement,
                'old_val': self.article_ids[2].old_val,
                'revision_val': self.article_ids[2].revision_val,
                'contract_id': contrat.id,
            })
            i += 1
        # remunération
        if self.remuneration_ok:
            if self.contract_id.categorie:
                cat1 = self.contract_id.categorie
            else:
                cat1 = '-'
            if self.contract_id.section:
                sec1 = self.contract_id.section
            else:
                sec1 = '-'
            if self.categorie:
                cat2 = self.categorie
            else:
                cat2 = '-'
            if self.section:
                sec2 = self.section
            else:
                sec2 = '-'
            self.env['hr.contract.avenant.line'].create({
                'name': '0' + str(i),
                'article': self.article_ids[3].article,
                'type_changement': self.article_ids[3].type_changement,
                'old_val': 'Salaire ' + str(self.contract_id.wage) + ' - [' + cat1 + '/' + sec1 + ']',
                'revision_val': 'Salaire ' + str(self.wage) + ' - [' + cat2 + '/' + sec2 + ']',
                'contract_id': contrat.id,
            })
            contrat.rubrique_ids.unlink()
            for rec in self.rubrique_ids:
                self.env['hr.contract.rubrique'].create({
                    'name': rec.name,
                    'contract_id': contrat.id
                })
            if self.wage > 0:
                contrat.wage = self.wage

        # mise a jour ancien contrat et fiche employé
        self.contract_id.state = 'cancel'
        self.employee_id.job_id = job
        self.employee_id.department_id = department

        return {
            'name': 'Avenant',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.contract',
            'target': 'current',
            'res_id': contrat.id,
        }


class CreerAvenantWizardLine(models.TransientModel):
    _name = 'create.avenant.wizard.line'

    @api.depends('type_changement')
    def _get_old_val(self):
        for rec in self:
            if rec.type_changement == 'fonction':
                rec.old_val = rec.wiz_id.contract_id.job_id.name
            elif rec.type_changement == 'affectation':
                rec.old_val = rec.wiz_id.contract_id.department_id.name
            elif rec.type_changement == 'engagement':
                if rec.wiz_id.contract_id.date_end:
                    d_end = ' au ' + str(rec.wiz_id.contract_id.date_end.strftime('%d-%m-%Y'))
                else:
                    d_end = ''
                rec.old_val = 'du ' + str(rec.wiz_id.contract_id.date_start.strftime('%d-%m-%Y')) + d_end
            else:
                rec.old_val = ''

    name = fields.Char('Artilce avenant')
    article = fields.Char('Numéro article modifié')
    type_changement = fields.Selection([('engagement', 'L\'engagement'),
                                        ('fonction', 'La fonction'),
                                        ('affectation', 'L\'affectation'),
                                        ('remuneration', u'La rémunération'), ], string='type changement')
    old_val = fields.Char(compute=_get_old_val, string='Actuellement')
    revision_val = fields.Char('Révisé comme...')
    wiz_id = fields.Many2one('create.avenant.wizard')


class CreerAvenantWizardRubrique(models.TransientModel):
    _name = 'create.avenant.wizard.rubrique'
    _description = 'Rubrique'

    name = fields.Char('Rubrique')
    wiz_id = fields.Many2one('create.avenant.wizard')
