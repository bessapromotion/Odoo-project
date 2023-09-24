from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import UserError
import time


class SalesReportBySalesperson(models.TransientModel):
    _name = 'sale.salesperson.report'

    start_date = fields.Datetime(string="Date début", required=True)
    end_date = fields.Datetime(string="Date fin", required=True, default=datetime.today())
    salesperson_ids = fields.Many2many('res.users', string="Commercial(e)s", required=True)

    # @api.multi
    def print_sale_report_by_salesperson(self):
        sales_order = self.env['sale.order'].search([('state', '=', 'sale')])
        sale_order_groupby_dict = {}

        if self.start_date > self.end_date:
            raise UserError(
                _('Erreur de date  ! \n\n  La date de début doit être inférieur ou égale à la date de fin !'))

        self.start_date = datetime(self.start_date.year, self.start_date.month, self.start_date.day, 0, 0, 0)
        self.end_date = datetime(self.end_date.year, self.end_date.month, self.end_date.day, 22, 59, 59)

        for salesperson in self.salesperson_ids:
            filtered_sale_order = list(filter(lambda x: x.user_id == salesperson, sales_order))
            print('filtered_sale_order ===', filtered_sale_order)
            filtered_by_date = list(filter(lambda x: x.date_order >= self.start_date and x.date_order <= self.end_date,
                                           filtered_sale_order))
            sale_order_groupby_dict[salesperson.name] = filtered_by_date

        final_dist = {}
        for salesperson in sale_order_groupby_dict.keys():
            sale_data = []
            for order in sale_order_groupby_dict[salesperson]:
                temp_data = []
                temp_data.append(order.name)
                temp_data.append(order.project_id.name)
                temp_data.append(order.num_dossier)
                temp_data.append(order.date_order)
                temp_data.append(order.partner_id.name)
                temp_data.append(order.amount_total)
                temp_data.append(order.state)
                temp_data.append(order.origin)
                sale_data.append(temp_data)
            final_dist[salesperson] = sale_data
        datas = {
            'ids': self,
            'model': 'sale.salesperson.report',
            'form': final_dist,
            'start_date': self.start_date,
            'end_date': self.end_date
        }
        return self.env.ref('rapports_ventes.action_report_by_salesperson').report_action([], data=datas)


class SalesReportByProject(models.TransientModel):
    _name = 'sale.project.report'

    start_date = fields.Datetime(string="Date début", required=True)
    end_date = fields.Datetime(string="Date fin", required=True, default=datetime.today())
    project_ids = fields.Many2many('project.project', string="Projets", required=True)

    # @api.multi
    def print_sale_report_by_project(self):
        sales_order = self.env['sale.order'].search([('state', '=', 'sale')])
        sale_order_groupby_dict = {}

        if self.start_date > self.end_date:
            raise UserError(
                _('Erreur de date  ! \n\n  La date de début doit être inférieur ou égale à la date de fin !'))

        self.start_date = datetime(self.start_date.year, self.start_date.month, self.start_date.day, 0, 0, 0)
        self.end_date = datetime(self.end_date.year, self.end_date.month, self.end_date.day, 22, 59, 59)

        for project in self.project_ids:
            filtered_sale_order = list(filter(lambda x: x.project_id == project, sales_order))
            print('filtered_sale_order ===', filtered_sale_order)
            filtered_by_date = list(filter(lambda x: x.date_order >= self.start_date and x.date_order <= self.end_date,
                                           filtered_sale_order))
            sale_order_groupby_dict[project.name] = filtered_by_date

        final_dist = {}
        for project in sale_order_groupby_dict.keys():
            sale_data = []
            for order in sale_order_groupby_dict[project]:
                temp_data = []
                temp_data.append(order.name)
                temp_data.append(order.user_id.name)
                temp_data.append(order.num_dossier)
                temp_data.append(order.date_order)
                temp_data.append(order.partner_id.name)
                temp_data.append(order.amount_total)
                temp_data.append(order.state)
                temp_data.append(order.origin)
                sale_data.append(temp_data)
            final_dist[project] = sale_data
        datas = {
            'ids': self,
            'model': 'sale.project.report',
            'form': final_dist,
            'start_date': self.start_date,
            'end_date': self.end_date
        }
        return self.env.ref('rapports_ventes.action_report_by_project').report_action([], data=datas)


class PaiementParMode(models.TransientModel):
    _name = 'paiement.report'

    # @api.model
    # def get_mode_paiements(self): return = self.env['mode.paiement'].search([])

    start_date = fields.Date(string="Date début", required=True, default=date.today())
    end_date = fields.Date(string="Date fin", required=True, default=date.today())
    mode_paiement_ids = fields.Many2many('mode.paiement', string="Modes de paiement", required=True)

    # @api.multi
    def print_paiement_par_mode(self):
        ordre_paiement = self.env['ordre.paiement'].search([])
        ordre_paiement_groupby_dict = {}

        if self.start_date > self.end_date:
            raise UserError(
                _('Erreur de date  ! \n\n  La date de début doit être inférieur ou égale à la date de fin !'))

        self.start_date = date(self.start_date.year, self.start_date.month, self.start_date.day)
        self.end_date = date(self.end_date.year, self.end_date.month, self.end_date.day)

        for mode_paiement in self.mode_paiement_ids:
            # Filtrer la listes des paiements par Mode de paiement
            filtered_ordre_paiement = list(filter(lambda x: x.mode_paiement_id == mode_paiement, ordre_paiement))

            print('filtered_ordre_paiement ===', filtered_ordre_paiement)
            # Filtrer la listes des paiements par date d'opération
            filtered_by_date = list(
                filter(lambda x: x.date >= self.start_date and x.date <= self.end_date, filtered_ordre_paiement))
            # éléminer les opérations annulées
            filtered_by_state = list(filter(lambda x: x.state != 'cancel', filtered_by_date))

            ordre_paiement_groupby_dict[mode_paiement.name] = filtered_by_state

        final_dist = {}
        for mode_paiement in ordre_paiement_groupby_dict.keys():
            paiement_data = []
            for op in ordre_paiement_groupby_dict[mode_paiement]:
                temp_data = []
                temp_data.append(op.name)
                temp_data.append(op.project_id.name)  # PROJECT
                temp_data.append(op.order_id.num_dossier)  # DOSSIER
                temp_data.append(op.date)
                temp_data.append(op.partner_id.name)  # CLIENT
                temp_data.append(op.mode_paiement_id.name)  #
                temp_data.append(op.doc_payment_id.name)
                temp_data.append(op.commercial_id.name)  # temp_data.append(op.doc_payment_id.name)
                temp_data.append(op.amount)
                temp_data.append(op.create_uid.name)
                paiement_data.append(temp_data)
            final_dist[mode_paiement] = paiement_data
        datas = {
            'ids': self,
            'model': 'paiement.report',
            'form': final_dist,
            'start_date': self.start_date,
            'end_date': self.end_date
        }
        return self.env.ref('rapports_ventes.action_paiement_par_mode').report_action([], data=datas)
