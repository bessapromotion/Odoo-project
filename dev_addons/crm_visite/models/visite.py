# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VisiteTags(models.Model):
    _name = 'visite.tags'
    _description = 'Tags'

    name = fields.Char('Tag', required=True)
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag existe deja !"),
    ]


class VisiteObs(models.Model):
    _name = 'visite.obs'
    _description = 'Observations'

    name = fields.Char('Observation', required=True)


class CrmVisite(models.Model):
    _name = 'crm.visite'
    _description = 'Visite'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'heure_entree desc'

    # @api.one
    @api.depends('opportunity_id')
    def _has_opportunity(self):
        for rec in self:
            if rec.opportunity_id:
                rec.has_opportunity = True
            else:
                rec.has_opportunity = False

    name = fields.Many2one('res.partner', string='Client')
    etat = fields.Selection(related='name.etat', string='Status')
    mobile = fields.Char(related='name.mobile', string='Mobile')
    date = fields.Date('Date', default=lambda self: fields.Date.today())
    badge = fields.Char(u'Numéro Badge', required=False)
    source_id = fields.Many2one('utm.source', string='Source')
    user_demand = fields.Many2one('res.users', string=u'Commercial demandé')
    user_charge = fields.Many2one('res.users', string=u'Commercial chargé')
    observation = fields.Many2one('visite.obs', string='Observation', tracking=True)
    heure_entree = fields.Datetime(u'Heure entrée', required=True, tracking=True)
    heure_recu = fields.Datetime('Recu à ', tracking=True)
    heure_sortie = fields.Datetime('Heure sortie', tracking=True)
    obs_hubspot = fields.Char('Observation HUBSPOT', tracking=True)
    tags_ids = fields.Many2many('visite.tags', string='Etiquettes')
    opportunity_id = fields.Many2one(comodel_name='crm.lead', string=u'Opportunité', tracking=True,
                                     readonly=1)
    has_opportunity = fields.Boolean(compute=_has_opportunity, string='Opportunité')
    type_visite = fields.Selection([('Commercial', 'Commercial'), ('Employee', u'Employé'), ], default='Commercial')
    employee = fields.Many2one('hr.employee', string=u'Employé')
    visiteur_empl = fields.Char('Visiteur')
    state = fields.Selection([('valid', u'Effectuée'),
                              ('cancel', u'Annulée'), ], string='Etat', default='valid', tracking=True)

    @api.onchange('name')
    def onchange_client(self):
        if self.name and self.type_visite == 'Employee':
            self.visiteur_empl = self.name.name

    # @api.multi
    def convert_opportunity(self, partner_id=False,
                            planned_revenue=0.0, probability=0.0):
        partner = self.env['res.partner']
        opportunity = self.env['crm.lead']
        opportunity_dict = {}
        default_contact = False
        for call in self:
            if not partner_id:
                partner_id = call.name.id or False
            if partner_id:
                address_id = partner.address_get().get('contact', False)
                if address_id:
                    default_contact = address_id.id
            opportunity_id = opportunity.create({
                'name': call.observation,
                'expected_revenue': planned_revenue,
                'probability': probability,
                'partner_id': partner_id or False,
                'mobile': default_contact and default_contact.mobile,
                'description': call.observation or False,
                'user_id': call.user_charge.id,
                'type': 'opportunity',
                # 'phone': call.partner_phone or False,
                # 'email_from': default_contact and default_contact.email,
                # 'campaign_id': call.campaign_id.id,
                # 'source_id': call.source_id.id,
                # 'medium_id': call.medium_id.id,
                # 'tag_ids': [(6, 0, call.tags_ids.ids)],
            })
            vals = {
                # 'partner_id': partner_id,
                'opportunity_id': opportunity_id.id,
            }
            call.write(vals)
            opportunity_dict[call.id] = opportunity_id
        return opportunity_dict

    # @api.multi
    def action_button_convert2opportunity(self):
        if self.observation:
            opportunity_dict = {}
            for visite in self:
                opportunity_dict = visite.convert_opportunity()
                return opportunity_dict[visite.id].redirect_lead_opportunity_view()
            return opportunity_dict
        else:
            raise UserError(_(u'Veuillez saisir une observation pour donner un titre à l\'opportunité'))

    # @api.multi
    def unlink(self):
        raise UserError(_(u'Suppression non autorisée ! \n\n  Si la visite est valide vous pouvez l''annuler !'))

    # @api.one
    def action_cancel(self):
        self.state = 'cancel'


class CrmVocale(models.Model):
    _name = 'crm.vocale'
    _description = 'Boite vocale'
    _order = 'heure_appel desc'

    name = fields.Many2one('res.partner', string='Client')
    etat = fields.Selection(related='name.etat', string='Status')
    # status_client = fields.Many2one('utm.')
    date = fields.Date('Date')
    phone = fields.Char('Numéro de téléphone')
    user_id = fields.Many2one('res.users', string='Commercial')
    heure_appel = fields.Datetime('Heure appel')
    observation = fields.Char('Observation')
    feedback = fields.Char('Feedback')
    tags_ids = fields.Many2many('visite.tags', string='Etiquettes')
