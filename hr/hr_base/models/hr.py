# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError


class HrTypePlacement(models.Model):
    _name = 'hr.type.placement'
    _description = 'Type placement'

    name = fields.Char('Type placement', required=1)


class Civilite(models.Model):
    _name = 'hr.civilite'
    _description = 'Civilité'

    name = fields.Char(u'Civilité', required=1)
    code = fields.Char('Code')

    _sql_constraints = [('name_uniq', 'unique (name)', "Civilité existe déjà !"), ]


class CSP(models.Model):
    _name = 'hr.csp'
    _description = 'Catégorie SocioProfessionnelle'

    name = fields.Char(u'Catégorie', required=1)

    _sql_constraints = [('name_uniq', 'unique (name)', "Catégorie existe déjà !"), ]


class Hr(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    @api.depends('historique_ids')
    def _nbr_operations(self):
        for rec in self:
            rec.nbr_doc = len(rec.historique_ids)

    def generate_matricule(self):
        for rec in self:
            print(str(rec.company_id.matricule_employeur) + '-' + str(self.env['ir.sequence'].get('hr.employee')))
            rec.matricule = str(rec.company_id.matricule_employeur) + '-' + str(
                self.env['ir.sequence'].get('hr.employee'))

    civilite_id = fields.Many2one('hr.civilite', string=u'Civilité')
    matricule_old = fields.Char('Ancien Matricule')
    matricule = fields.Char('Matricule', )
    id_pointeuse = fields.Char('Identifiant de la pointeuse', )
    id_carte = fields.Char('Identifiant de la carte Pro', )
    type_placement_id = fields.Many2one('hr.type.placement', 'Type placement', )

    csp_id = fields.Many2one('hr.csp', string='Cat. SocioProfessionnelle')
    pi_type = fields.Selection([('cin', 'Carte identitité nationale'), ('pc', 'Permis de conduire'), ],
                               string=u'Type pièce identité', default='cin')
    pi_num = fields.Char(u'Numéro PI', size=18)
    pi_date = fields.Date(u'Délivrée le ')
    pi_par = fields.Char('Par')
    act_naissance = fields.Char(u'Numéro acte de naissance')
    presume = fields.Boolean(u'Présumé')
    emp_declare = fields.Boolean(u'Employé Décalré')
    # matricule = fields.Char(related='barcode', string='Matricule', readonly=1)
    adresse_simple = fields.Char(u'Adresse', translate=True)
    residence_commune = fields.Many2one('res.commune', string=u'Commune de résidence',
                                        domain="[('state_id', '=?', residence_wilaya_id)]")
    residence_wilaya_id = fields.Many2one('res.country.state', string=u'Wilaya de résidence',
                                          domain=[('country_id', '=?', 62)])

    grp_sanguin = fields.Selection([('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'),
                                    ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], string='Groupe Sanguin')
    telephone = fields.Char(string='Télephone')
    email = fields.Char(string='Email')
    name_jf = fields.Char(u'Nom jeune fille')
    name_arab = fields.Char(u'Nom Prénom (en arabe)')
    prenom_pere = fields.Char(u'Prénom du pére')
    nom_prenom_mere = fields.Char(u'Nom et prénom de la mére')
    ss_num = fields.Char(u'Numéro SS', size=12)
    mariage_date = fields.Date('Date mariage')
    mariage_acte = fields.Char('Acte mariage')
    wilaya_naissance_id = fields.Many2one('res.country.state', string='Wilaya de naissance')
    emergency_nature = fields.Char('Nature du contact')
    # site_id = fields.Many2one('res.partner', string='Affectation')

    compte_num = fields.Char('Numéro de compte', size=20)
    compte_nature = fields.Selection([('CCP', 'CCP'), ('Banque', 'Banque')], string='Nature du compte', default='CCP')
    rib = fields.Char('RIB', size=20)
    compte_domiciliation = fields.Char('Domiciliation')

    carte_sejour = fields.Char('N° Carte de séjour')

    # info attestation et certificat
    motif_attestation = fields.Char(u'Motif délivrance attestation de travail')
    num_attestation = fields.Char('Numero attestation de travail', default='/', readonly=1)
    num_attestation_req = fields.Char('Numero seq attestation de travail', default='/', readonly=1)
    num_certificat = fields.Char('Numero certificat de travail', default='/', readonly=1)
    num_certificat_req = fields.Char('Numero seq certificat', default='/', readonly=1)
    num_fgp = fields.Char('Numero Fiche de Gestion Personnel', default='/', readonly=1)
    num_fgp_req = fields.Char('Numero seq fiche de gestion personnel', default='/', readonly=1)
    user_print = fields.Char('User')

    historique_ids = fields.One2many('hr.employee.historique', 'employe_id', string='Historique')
    nbr_doc = fields.Integer(compute=_nbr_operations, string=u'Nombre opérations')
    num_embauche = fields.Integer('Num Embauche', default=1, readonly=1)
    address_ar = fields.Char(string="Adresse en Arabe")

    # Translatable fields
    place_of_birth = fields.Char(translate=True)

    # Overide du champ aulieu d'utiliser selection_add a cause de l'ordre des items
    certificate = fields.Selection([
        ('moyen', 'Moyen'),
        ('secondaire', 'Secondaire'),
        ('license', 'License'),
        ('graduate', 'Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ], 'Certificate Level', default='other', groups="hr.group_hr_user", tracking=True)

    def _matricule_no_duplicates(self):
        dupes = self.env['hr.employee'].search([('barcode', '=', self.barcode), ('id', '!=', self.id)])
        if dupes and not self.barcode:
            raise UserError(_(u'le matricule employé existe déja!'))

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            self.job_title = self.job_id.name
            self.csp_id = self.job_id.csp_id.id

    def print_attestation_travail(self):
        if self.contract_id:
            # corriger contrat
            ctr = self.env['hr.contract'].search([('state', '=', 'open')])
            for rec in ctr:
                rec.employee_id.contract_id = rec.id

            num = self.env['ir.sequence'].get('hr.employee.at')

            self.num_attestation = self.env['ir.sequence'].get('hr.employee.at') or '/'
            self.num_attestation_req = num + '_' + str(date.today())[:4]

            self.env['hr.employee.historique'].create({
                'employe_id': self.id,
                'document': u'Impression attestation de travail',
                'numero': self.num_attestation,
                'date_doc': date.today(),
                'user_id': self.env.user.id,
                'note': u'Document joint à la fiche employé',
                'model_name': 'hr.employee',
                'model_id': self.id,
                'num_embauche': self.num_embauche,
            })
            return self.env.ref('hr_base.act_report_attestation_travail').report_action(self)

            # return {
            #     'name': _('Motif delivrance attestation de travail'),
            #     'view_mode': 'form',
            #     'res_model': 'motif.attestation.wizard',
            #     'view_id': self.env.ref('hr_base.motif_attestation_wizard_form_view').id,
            #     'type': 'ir.actions.act_window',
            #     'context': {
            #         'default_name': self.id,
            #         'default_state': '1',
            #     },
            #     'target': 'new',
            # }
        else:
            raise UserError(_(u'''L'employé doit avoir un contrat !'''))

    def print_certificat_travail(self):
        if self.contract_id:
            for rec in self.contract_ids:
                if not rec.date_end:
                    raise UserError(_(
                        'La date fin d\'un des contrats ou avenant n\'est pas reseignée, \n'
                        'Veuillez completer les informations du contrat et mettre a jour son état avant l\'impression du certificat'))

            num = self.env['ir.sequence'].get('hr.employee.ct') or '/'
            self.num_certificat = self.env['ir.sequence'].get('hr.employee.ct') or '/'
            self.num_certificat_req = num + '_' + str(date.today())[:4]

            self.env['hr.employee.historique'].create({
                'employe_id': self.id,
                'document': u'Impression certificat de travail',
                'numero': self.num_certificat,
                'date_doc': date.today(),
                'user_id': self.env.user.id,
                'note': u'Document joint à la fiche employé',
                'model_name': 'hr.employee',
                'model_id': self.id,
                'num_embauche': self.num_embauche,
            })

            return self.env.ref('hr_base.act_report_certificat_travail').report_action(self)
        else:
            raise UserError(_(u'''L'employé doit avoir un contrat !'''))

    def print_fgp(self):
        num = self.env['ir.sequence'].get('hr.employee.fgp')
        self.num_fgp = num + '/MIN/' + str(date.today())[:4]
        self.num_fgp_req = num + '_' + str(date.today())[:4]

        return self.env.ref('hr_base.act_report_fgp').report_action(self)


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    name = fields.Char(translate=True)
