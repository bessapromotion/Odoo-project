# -*- coding: utf-8 -*-

from odoo import models, fields, _
from datetime import datetime
from xlrd import open_workbook
import xlrd
from odoo.exceptions import UserError
import base64
import logging
_logger = logging.getLogger(__name__)


# récuperer la valeur d'une cellule [row, col] sur la feuille excel sh
def _supp_dot_0(val):
    v = str(val)
    if len(v) > 2:
        if v[-2:] == '.0':
            v = v[:-2]
    return v


# récuperer la valeur d'une cellule [row, col] sur la feuille excel sh
def _get_cell(sh, row, col, st=False):
    if col == -1:
        return None
    else:
        value = sh.cell(row, col).value
        if st:
            value = str(value)
            if value[-2:] == '.0':
                value = value[:-2]
        return value


# vérifie si la valeur de la cellule est vide
def _check_not_null(sh, row, col, name_field):
    value = sh.cell(row, col).value
    if value and value != '':
        return True
    else:
        raise UserError(_(
            'Erreur a la ligne '+str(row+1)+', Le champs ('+name_field+') est vide, veuillez corriger sur le fichier excel et relancer l\'importation'))


def read_file(fname):
    # copier le fichier selectionné (Field.Binary) dans un fichier temporaire (avec un chemin connu) et utiliser le fichier tmp
    file_path = 'tmp/file.xlsx'
    data = fname
    f = open(file_path, 'wb')
    # f.write(data.decode('base64')) #  Python 2.7
    f.write(base64.b64decode(data))  # - pour python 3, rajouter aussi import base64

    f.close()
    return file_path


def get_col_num(col_name):
    if col_name:
        return ord(col_name) - 65
    else:
        return -1


class ImportLeadsWizard(models.TransientModel):
    _name = 'import.leads.wizard'

    name          = fields.Char    ('Importation des produits', default='/')
    w_file_name   = fields.Binary  ('Sélectionnez le document', required=True)
    filename      = fields.Char    ('Filename')
    print_report = fields.Boolean('Afficher un rapport d\'erreur', default=True)
    error = fields.Boolean('Erreur')
    cntrl_only = fields.Boolean('Faire un controle seulement')
    state = fields.Selection([('new', u'Sélectionnez une opération'),
                              ('lead', 'Importer Leads'),
                              ('crm', 'Importer des transactions'),
                              ('payment', 'Importer des recouvrements'),
                              ], string='Operation', default='new')
    # lead
    model2_id     = fields.Many2one('leads.import.model', string='Modele d\'importation', required=False, states={'lead': [('required', True)]})
    lifecycle_ids = fields.Many2many('crm.lifecycle', string='Importer les etats')

    def elem_exist_req(self, model, nfield, value):
        if model == 'product_product':
            req = "select count(*)  as nbr from product_product, product_template where product_template.name =%s and product_template.id = product_product.product_tmpl_id"
        else:
            req = "select count(*) as nbr from " + model + " where " + nfield + "=%s;"
        rub = (value,)
        self._cr.execute(req, rub)
        res = self._cr.dictfetchall()
        num = res[0].get('nbr')
        if not num or num == 0:
            return False
        else:
            return True

    def check_exist(self, sh, row, col, model, nfield, name_field, fich, print_rep=False):
        field_val = str(sh.cell(row, col).value)
        if field_val:
            if field_val[-2:] == '.0':
                field_val = field_val[:-2]
            # mat = self.env[model].search([(nfield, '=', field_val)])
            if not self.elem_exist_req(model, nfield, field_val):
                self.error = True
                msg = 'Erreur a la ligne ' + str(
                            row + 1) + ', Le ' + name_field + ' [' + _supp_dot_0(field_val)+'] n\'existe pas sur la base Odoo, veuillez corriger sur le fichier excel ou créer cet élément puis relancer l\'importation'
                if not print_rep:
                    raise UserError(_(msg))
                else:
                    fich.write(str(row + 1) + ';' + name_field + ';' + _supp_dot_0(field_val) + '\n')

    def get_field_id(self, sh, row, col, model, nfield):
        if col == -1:  # la colonne n'existe pas sur excel
            return None
        else:
            field_val = str(sh.cell(row, col).value)
            if field_val:
                if field_val[-2:] == '.0':
                    field_val = field_val[:-2]
                mat = self.env[model].search([(nfield, '=', field_val)])
                if mat.exists():
                    return mat[0].id
                else:
                    return None
            else:  # la colonne existe mais elle n'est pas renseignée
                return None

    def action_import_lead(self):

        def verify_data(sh):
            for row in range(1, sh.nrows):
                # _check_not_null(sh, row, MODEL_NUMERO_PIECE, 'Numéro Piéce')
                # _check_not_null(sh, row, MODEL_DATE, 'Date')
                # _check_not_null(sh, row, MODEL_JOURNAL, 'Journal')
                # _check_exist(sh, row, MODEL_JOURNAL, 'account_journal', 'code', 'Journal', self.print_report)
                # _check_exist(sh, row, MODEL_TIERS, 'res_partner', 'code_tiers', 'Tiers', self.print_report)
                # _check_not_null(sh, row, MODEL_COMPTE, 'Compte')
                self.check_exist(sh, row, MODEL_OWNER, 'res_users', 'hubspot', 'HubSpot Owner name', fid, self.print_report)

        def create_partner(sheet):
            partner_id = self.get_field_id(sheet, row_index, MODEL_ID, 'res.partner', 'hs_contact_id')

            if not partner_id:
                lc = self.env['crm.lifecycle'].search([('name', '=', _get_cell(sheet, row_index, MODEL_STAGE))])
                if lc.exists():
                    etat = lc.etat
                    progression = lc.crm_stage_id.probability
                    stage = lc.crm_stage_id.id
                else:
                    etat = 'Prospect'
                    progression = 0
                    stage = 1

                client = self.env['res.partner'].create({
                    'name'         : _get_cell(sheet, row_index, MODEL_NOM) + ' ' + _get_cell(sheet, row_index, MODEL_PRENOM),
                    'display_name' : _get_cell(sheet, row_index, MODEL_NOM) + ' ' + _get_cell(sheet, row_index, MODEL_PRENOM),
                    'user_id'      : self.get_field_id(sheet, row_index, MODEL_OWNER, 'res.users', 'hubspot'),
                    'customer'     : True,
                    'supplier'     : False,
                    'street'       : _get_cell(sheet, row_index, MODEL_ADRESSE),
                    'email'        : _get_cell(sheet, row_index, MODEL_EMAIL),
                    'phone'        : _get_cell(sheet, row_index, MODEL_PHONE),
                    'hs_contact_id': _get_cell(sheet, row_index, MODEL_ID),
                    'etat'         : etat,
                    'is_company'   : False,
                })
                # lead
                self.env['crm.lead'].create({
                    'name'        : client.name,
                    'contact_name': client.name,
                    'partner_id'  : client.id,
                    'type'        : 'opportunity',
                    'user_id'     : client.user_id.id,
                    'probability' : progression,
                    'stage_id'    : stage,
                    'mobile'      : _get_cell(sheet, row_index, MODEL_PHONE),
                    'referred'    : 'Importé depuis HubSpot',
                })

        # début opération
        # parametre des numeros des colonnes
        MODEL_ID      = self.model2_id.col_id
        MODEL_NOM     = self.model2_id.col_nom
        MODEL_PRENOM  = self.model2_id.col_prenom
        # MODEL_DATE    = self.model2_id.col_date
        MODEL_ADRESSE = self.model2_id.col_adresse
        MODEL_PHONE   = self.model2_id.col_phone
        MODEL_EMAIL   = self.model2_id.col_email
        MODEL_STAGE   = self.model2_id.col_stage
        MODEL_OWNER   = self.model2_id.col_owner

        # ouvrir excel
        book   = open_workbook(read_file(self.w_file_name))
        xsheet = book.sheet_by_index(0)

        # pour ecrire les erreurs d'importation sur un fichier csv
        if self.print_report:
            fid = open('tmp/erreur_importation.csv', 'w')
            fid.write('Ligne;Table;Valeur Non trouvé \n')

        # _logger.info("--------------------lancement------------------------------------- ")
        # verifier s'il n y a d'erreur ou de manque dans le fichier excel a importer

        self.error = False
        verify_data(xsheet)
        if self.print_report:
            fid.close()
        # _logger.info("--------------------verification-----ok------------------------------ ")

        # debut du traitmnt
        if self.error:
            if self.print_report:
                raise UserError(_('Fichier contient des anomalies, veuillez consulter le fichier log généré [erreur_importation.csv]'))
        else:
            if self.cntrl_only:
                raise UserError(_('Tout est OK'))

            for row_index in range(1, xsheet.nrows):
                lc = self.env['crm.lifecycle'].search([('name', '=', _get_cell(xsheet, row_index, MODEL_STAGE))])
                if lc.exists():
                    if lc in self.lifecycle_ids:
                        _logger.info("---ligne------------------------------------- : %s ", row_index)
                        create_partner(xsheet)

    def action_import_crm(self):

        def verify_data(sh):
            for row in range(1, sh.nrows):
                _check_not_null(sh, row, MODEL_RECOUV, 'Chargé du recouvrement')
                _check_not_null(sh, row, MODEL_COMMERC, 'Commercial')
                _check_not_null(sh, row, MODEL_NAME, 'Bien')
                _check_not_null(sh, row, MODEL_PARTNER, 'Client')
                # _check_exist(sh, row, MODEL_JOURNAL, 'account_journal', 'code', 'Journal', self.print_report)
                # _check_exist(sh, row, MODEL_TIERS, 'res_partner', 'code_tiers', 'Tiers', self.print_report)
                # _check_not_null(sh, row, MODEL_COMPTE, 'Compte')
                self.check_exist(sh, row, MODEL_RECOUV, 'res_users', 'login', 'Chargé du recouvrement', fid, self.print_report)
                self.check_exist(sh, row, MODEL_COMMERC, 'res_users', 'login', 'Commercial', fid, self.print_report)
                self.check_exist(sh, row, MODEL_NAME, 'product_product', 'name', 'Bien', fid, self.print_report)
                self.check_exist(sh, row, MODEL_PARTNER, 'res_partner', 'name', 'Client', fid, self.print_report)

        def create_order(sheet):
            # mise a jour fiche article
            bien_id.product_tmpl_id.prix_m2 = _get_cell(sheet, row_index, MODEL_PU_B)
            bien_id.etat = 'Pré-Réservé'
            bien_id.client_id = partner_id.id
            bien_id.num_lot = _get_cell(sheet, row_index, MODEL_LOT, True)
            partner_id.etat = 'Potentiel'

            if partner_id:
                order = self.env['sale.order'].create({
                    'origin'       : partner_id.name,
                    'create_auto'  : True,
                    'state'        : 'draft',
                    'date_order'   : py_date,
                    'validity_date': py_date,
                    'confirmation_date': py_date,
                    'user_id'      : commercial_id,
                    'partner_id'   : partner_id.id,
                    'company_id'   : self.env.user.company_id.id,
                    'team_id'      : 1,
                    'payment_term_id': 1,
                    # 'opportunity_id': ,
                    'project_id'   : bien_id.project_id.id,
                    'num_dossier'  : _get_cell(sheet, row_index, MODEL_DOSSIER, True),
                    # 'order_line'   : [(4, 0, lines)],
                })

                lines = []
                # self.env['sale.order.line'].create({
                lines.append({
                    # 'order_id'  : order.id,
                    'name'      : _get_cell(sheet, row_index, MODEL_NAME),
                    'sequance'  : 10,
                    'price_unit': _get_cell(sheet, row_index, MODEL_PRICE),
                    'price_subtotal': _get_cell(sheet, row_index, MODEL_PRICE),
                    'prix_m2': _get_cell(sheet, row_index, MODEL_PU_B),
                    'price_tax' : 0.0,
                    'price_total': _get_cell(sheet, row_index, MODEL_PRICE),
                    'product_id': bien_id.id,
                    'product_uom_qty': 1.0,
                    'product_uom': 1,
                    'salesman_id': partner_id.user_id.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'company_id': self.env.user.company_id.id,
                    'order_partner_id': partner_id.id,
                    'state': 'draft',
                })
                order.order_line = lines
                bien_id.order_id = order.id
                bien_id.list_price = _get_cell(sheet, row_index, MODEL_PRICE)
                # order.product_id_change()
                # order.product_uom_change()
                # order._compute_invoice_status()
                # order._compute_amount()
                # order._get_to_invoice_qty()
                # order._get_price_reduce()

                # confirmer le devis
                order.action_confirm()
                return order

        def create_reservation(order):
            reservation = self.env['crm.reservation'].create({
                'order_id' : order.id,
                'partner_id': partner_id.id,
                # 'invoice_id': invoice.id,
                'date': py_date.date(),
                'date_limite': py_date.date(),
                'commercial_id' : order.user_id.id,
                'charge_recouv_id' : order.user_id.id,
            })
            reservation.onchange_devis()
            reservation.state = 'valid'
            reservation.partner_id.etat = 'Réservataire'
            for rec in reservation.product_ids:
                rec.name.client_id = partner_id.id
                rec.name.etat = 'Réservé'
                rec.name.order_id = order.id
                rec.name.reservation_id = reservation.id
                # annuler tous les autres devis
                for dvs in rec.name.line_ids:
                    if dvs.order_id.name != order.name:
                        dvs.order_id.action_cancel()
                        if not dvs.order_id.motif_annulation:
                            dvs.order_id.motif_annulation = 'Prereservation'

            # début opération
        # parametre des numeros des colonnes
        MODEL_ID      = 0
        MODEL_NAME    = 2
        MODEL_DOSSIER = 3
        MODEL_LOT     = 4
        MODEL_PARTNER = 6
        MODEL_PU_B    = 8
        MODEL_PRICE   = 9
        # MODEL_PU_P    = 7
        # MODEL_QT_P    = 8
        # MODEL_PU_C    = 9
        # MODEL_QT_C    = 10
        MODEL_DATE    = 16
        MODEL_RECOUV  = 17
        MODEL_COMMERC = 18

        # ouvrir excel
        book   = open_workbook(read_file(self.w_file_name))
        xsheet = book.sheet_by_index(0)
        print('ici - ----- ' + xsheet.cell(1, 1).value)

        # pour ecrire les erreurs d'importation sur un fichier csv
        if self.print_report:
            fid = open('tmp/erreur_importation.csv', 'w')
            fid.write('Ligne;Table;Valeur Non trouvé \n')

        # _logger.info("--------------------lancement------------------------------------- ")
        # verifier s'il n y a d'erreur ou de manque dans le fichier excel a importer

        self.error = False
        verify_data(xsheet)
        if self.print_report:
            fid.close()
        # _logger.info("--------------------verification-----ok------------------------------ ")

        # debut du traitmnt
        if self.error:
            if self.print_report:
                raise UserError(_('Fichier contient des anomalies, veuillez consulter le fichier log généré [erreur_importation.csv]'))
        else:
            if self.cntrl_only:
                raise UserError(_('Tout est OK'))

            for row_index in range(1, xsheet.nrows):
                # creation devis
                _logger.info("---ligne------------------------------------- : %s ", row_index)
                py_date = datetime(
                    *xlrd.xldate.xldate_as_tuple(int(_get_cell(xsheet, row_index, MODEL_DATE)), book.datemode))

                partner_id = self.env['res.partner'].browse(self.get_field_id(xsheet, row_index, MODEL_PARTNER, 'res.partner', 'display_name'))
                bien_id = self.env['product.product'].browse(self.get_field_id(xsheet, row_index, MODEL_NAME, 'product.product', 'name'))
                recouv_id = self.get_field_id(xsheet, row_index, MODEL_RECOUV, 'res.users', 'login')
                commercial_id = self.get_field_id(xsheet, row_index, MODEL_COMMERC, 'res.users', 'login')

                devis = create_order(xsheet)
                # facture = create_invoice(devis)
                create_reservation(devis)

    def action_import_payment(self):

        def verify_data(sh):
            for row in range(1, sh.nrows):
                _check_not_null(sh, row, MODEL_COMMERCIAL, 'Commericial')
                _check_not_null(sh, row, MODEL_DATE, 'Date')
                _check_not_null(sh, row, MODEL_DOSSIER, 'Contrat')
                _check_not_null(sh, row, MODEL_PROJET, 'Projet')
                _check_not_null(sh, row, MODEL_AMOUNT, 'Montant')
                _check_not_null(sh, row, MODEL_MODE, 'Mode de paiement')

                self.check_exist(sh, row, MODEL_PROJET, 'project_project', 'name', 'Projet', fid, self.print_report)
                self.check_exist(sh, row, MODEL_RECOUV, 'res_users', 'login', 'Recouvrement', fid, self.print_report)
                self.check_exist(sh, row, MODEL_COMMERCIAL, 'res_users', 'login', 'Commercial', fid, self.print_report)
                self.check_exist(sh, row, MODEL_MODE, 'mode_paiement', 'name', 'Mode de paiement', fid, self.print_report)

        def create_echeance(sheet, order, ln, mtn=0.0):
            if ln == 1:
                etat = 'done'
                lib = 'Versement initial #1'
                mtn = _get_cell(sheet, row_index, MODEL_AMOUNT)
            else:
                if mtn == 0.0:
                    etat = 'done'
                    lib = 'Reglement tranche #' + str(ln)
                    mtn = _get_cell(sheet, row_index, MODEL_AMOUNT)
                else:
                    etat = 'open'
                    lib = 'Tranche complémentaire #' + str(ln)

            ech = self.env['crm.echeancier'].create({
                'name'             : '#' + str(ln),
                'label'            : lib,
                'state'            : etat,
                'date_prevue'      : py_date.date(),
                'date_paiement'    : py_date.date(),
                'montant_prevu'    : mtn,
                'observation'      : '',
                'order_id'         : order.id,
                'type'             : 'tranche',
            })
            return ech

        def create_ordre_paiement(sheet, ech):
            mode = self.env['mode.paiement'].browse(self.get_field_id(xsheet, row_index, MODEL_MODE, 'mode.paiement', 'name'))

            if mode.name != 'Espece':
                doc = self.env['payment.doc'].create({
                    'name' : _get_cell(sheet, row_index, MODEL_CHQ_NUM, True),
                    'domiciliation' : _get_cell(sheet, row_index, MODEL_BANQUE),
                    'ordonateur' : _get_cell(sheet, row_index, MODEL_ORDONATEUR),
                    'date' : py_date.date(),
                    'mode_paiement_id' : mode.id,
                })
                doc_id = doc.id
            else:
                doc_id = None

            op = self.env['ordre.paiement'].create({
                'echeance_id'      : ech.id,
                'state'            : 'done',
                'observation'      : '',
                'date'             : py_date.date(),
                'commercial_id'    : self.get_field_id(xsheet, row_index, MODEL_COMMERCIAL, 'res.users', 'login'),
                'amount'           : _get_cell(sheet, row_index, MODEL_AMOUNT),
                'order_id'         : ech.order_id.id,
                'mode_paiement_id' : mode.id,
                'objet'            : ech.label,
                'doc_payment_id'   : doc_id,
            })
            return op

        def create_payment(sheet, op):
            payment = self.env['account.payment'].create({
                'name'             : '',
                'state'            : 'draft',
                'payment_type'     : 'inbound',
                'payment_reference': '',
                # 'move_name'        : ,
                # 'invoice_ids': [(6, 0, inv_line.invoice_id.ids)],
                'payment_method_id': 1,
                'partner_id'       : op.partner_id.id,
                'partner_type'     : 'customer',
                'amount'           : _get_cell(sheet, row_index, MODEL_AMOUNT),
                'currency_id'      : op.order_id.currency_id.id,
                'payment_date'     : py_date.date(),
                'communication'    : '',
                'journal_id'       : 7,
                'payment_difference_handling': 'open',
                'mode_paiement_id' : op.mode_paiement_id.id,
                'p_reference'      : op.doc_payment_id.name,
                'paiement_concretisation': True,
                'doc_payment_id'   : op.doc_payment_id.id,
                'echeance_id' : op.echeance_id.id,
            })
            payment.post()

        # parametre des numeros des colonnes
        MODEL_COMMERCIAL   = 0
        MODEL_RECOUV       = 1
        MODEL_DOSSIER      = 2  # contrat
        MODEL_PROJET       = 3
        MODEL_CODE_PARTNER = 4
        MODEL_PARTNER      = 5
        MODEL_AMOUNT       = 6
        MODEL_MODE         = 7
        MODEL_DATE         = 8
        MODEL_BANQUE       = 9
        MODEL_CHQ_NUM      = 10
        MODEL_ORDONATEUR   = 11
        MODEL_ETAT         = 17

        # ouvrir excel
        book   = open_workbook(read_file(self.w_file_name))
        xsheet = book.sheet_by_index(0)

        # pour ecrire les erreurs d'importation sur un fichier csv
        if self.print_report:
            fid = open('tmp/erreur_importation.csv', 'w')
            fid.write('Ligne;Table;Valeur Non trouvé \n')

        # verifier s'il n y a d'erreur ou de manque dans le fichier excel a importer

        self.error = False
        verify_data(xsheet)
        if self.print_report:
            fid.close()

        # debut du traitmnt
        if self.error:
            if self.print_report:
                raise UserError(_('Fichier contient des anomalies, veuillez consulter le fichier log généré [erreur_importation.csv]'))
        else:
            if self.cntrl_only:
                raise UserError(_('Tout est OK'))

            line = 1
            contrat = ''
            total_paiement = 0
            order_id = None
            for row_index in range(1, xsheet.nrows):
                if contrat != _get_cell(xsheet, row_index, MODEL_DOSSIER, True):
                    # completer l'échéancier
                    if order_id:
                        if order_id.amount_untaxed > total_paiement:
                            create_echeance(xsheet, order_id, line+1, order_id.amount_untaxed - total_paiement)
                    # réinitialieser les variables
                    contrat = _get_cell(xsheet, row_index, MODEL_DOSSIER, True)
                    total_paiement = 0
                    line = 1
                else:
                    line += 1

                py_date  = datetime(*xlrd.xldate.xldate_as_tuple(int(_get_cell(xsheet, row_index, MODEL_DATE)), book.datemode))
                projet  = self.get_field_id(xsheet, row_index, MODEL_PROJET, 'project.project', 'name')
                order_id = self.env['sale.order'].search([('num_dossier', '=', contrat),
                                                          ('project_id', '=', projet)])

                if order_id.exists():
                    echeance       = create_echeance(xsheet, order_id, line)
                    total_paiement += _get_cell(xsheet, row_index, MODEL_AMOUNT)
                    ordre_paiement = create_ordre_paiement(xsheet, echeance)
                    create_payment(xsheet, ordre_paiement)
                else:
                    UserError(_('Commande liée au contrat ' + str(contrat) + ' du projet ' + str(projet)))
