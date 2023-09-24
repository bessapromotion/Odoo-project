# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class ChargerBienBlocWizard(models.TransientModel):
    _name = 'crm.superficie.bloc.wizard'

    name = fields.Char('Bloc')


class ChargerBienWizard(models.TransientModel):
    _name = 'crm.superficie.charger.bien'

    superficie_id = fields.Many2one('crm.superficie', string='Changement surfacique', readonly=1)
    project_id = fields.Many2one('project.project', required=1, string='Projet', readonly=1)
    type_bien_ids = fields.Many2many('product.type', string='Type de bien', required=True)
    etage_ids = fields.Many2many('product.etage', string='Etage')
    # bloc = fields.Char('Bloc')
    bloc_ids = fields.Many2many('crm.superficie.bloc.wizard', string='Bloc')
    state = fields.Selection([('step1', 'step1'), ('step2', 'step2')], default='step1')
    bien_ids = fields.One2many('crm.superficie.charger.bien.line.wizard', 'wiz_id')

    # a supprimer
    surf_habitable_edd = fields.Float('Surface habitable(EDD)')
    surf_utile_edd = fields.Float('Surface utile(EDD)')
    surf_habitable_com = fields.Float('Surface habitable(COM)')
    surf_utile_com = fields.Float('Surface utile(COM)')

    def action_autre_recherche(self):
        self.bien_ids.unlink()
        self.state = 'step1'
        return {
            'name': 'Charger les biens pour le changement surfaciques',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm.superficie.charger.bien',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    def action_search(self):
        self.bien_ids.unlink()
        bloc_lst = []
        for bl in self.bloc_ids:
            bloc_lst.append(bl.name)

        if self.etage_ids:
            prod = self.env['product.template'].search([('project_id', '=', self.project_id.id),
                                                        ('type_id', 'in', self.type_bien_ids.ids),
                                                        ('etage', 'in', self.etage_ids.ids),
                                                        ])
        else:
            prod = self.env['product.template'].search([('project_id', '=', self.project_id.id),
                                                        ('type_id', 'in', self.type_bien_ids.ids),
                                                        ])

        for rec in prod:
            if self.bloc_ids:
                if rec.bloc in bloc_lst:
                    self.env['crm.superficie.charger.bien.line.wizard'].create({
                        'name': rec.id,
                        'superficie': rec.superficie,
                        'wiz_id': self.id,
                    })
            else:
                self.env['crm.superficie.charger.bien.line.wizard'].create({
                    'name': rec.id,
                    'superficie': rec.superficie,
                    'wiz_id': self.id,
                })

        self.state = 'step2'
        return {
            'name': 'Charger les biens pour le changement surfaciques',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm.superficie.charger.bien',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    def action_appliquer(self):
        def get_price(prod):
            if prod:
                if prod.order_id:
                    line = prod.order_id.order_line.filtered(lambda t: prod.id == t.product_id.product_tmpl_id.id)
                    if line:
                        return line.prix_m2
                    else:
                        return prod.prix_m2
                else:
                    return prod.prix_m2

        self.superficie_id.product_ids.unlink()
        for rec in self.bien_ids:
            self.env['crm.superficie.line'].create({
                'name': rec.name.id,
                'superficie': rec.name.superficie,
                'superficie_new': rec.name.superficie,
                'superficie_id': self.superficie_id.id,
                'action': 'noaction',
                'num_lot': rec.name.num_lot,
                'bloc': rec.name.bloc,
                'numero': rec.name.numero,
                'etage': rec.name.etage.id,
                'orientation': rec.name.orientation.id,
                'type_id': rec.name.type_id.id,
                'format_id': rec.name.format_id.id,
                'state_grp': rec.name.etat,
                'bloc_grp': rec.name.bloc,
                'etage_grp': rec.name.etage.name,
                'prix_m2': get_price(rec.name),
                'prix_m2_new': get_price(rec.name),
            })
        self.superficie_id.state = 'progress'


class ChargerBienLineWizard(models.TransientModel):
    _name = 'crm.superficie.charger.bien.line.wizard'

    name = fields.Many2one('product.template', string='Appartement', readonly=1, required=True)
    superficie = fields.Float('Superficie', readonly=1)
    num_lot = fields.Char(related='name.num_lot', string='N° Lot', readonly=1)
    bloc = fields.Char(related='name.bloc', string='N° Bloc', readonly=1)
    numero = fields.Char(related='name.numero', string='N°', readonly=1)
    etage = fields.Many2one(related='name.etage', string='N° Etage', readonly=1)
    state = fields.Selection(related='name.etat', string='Etat du bien')
    order_id = fields.Many2one(related='name.order_id', string='Commande')
    num_dossier = fields.Char(related='name.order_id.num_dossier', string='Num Dossier')
    wiz_id = fields.Many2one('crm.superficie.charger.bien', string='Changement de superficie')

    # nouvelles infos
    type_id = fields.Many2one(related='name.type_id', string='Type du bien')
    orientation = fields.Many2one(related='name.orientation', string='Orientation')
    partner_id = fields.Many2one(related='name.client_id', string='Client')
    etat = fields.Selection(related='name.etat', string='Etat')
    format_id = fields.Many2one(related='name.format_id', string='Typologie')


class CrmChargerBienWizard(models.TransientModel):
    _name = 'crm.superficie.charger.bien.wizard'
