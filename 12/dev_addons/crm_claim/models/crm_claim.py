# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext


class CrmClaimStage(models.Model):
    _name = "crm.claim.stage"
    _description = "Claim stages"
    _rec_name = 'name'
    _order = "sequence"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', help="Used to order stages. Lower is better.",default=lambda *args: 1)
    team_ids = fields.Many2many('crm.team', 'crm_team_claim_stage_rel', 'stage_id', 'team_id', string='Teams',
                        help="Link between stages and sales teams. When set, this limitate the current stage to the selected sales teams.")
    case_default = fields.Boolean('Common to All Teams',
                        help="If you check this field, this stage will be proposed by default on each sales team. It will not assign this stage to existing teams.")

    _defaults = {
        'sequence': lambda *args: 1
    }                        


class CrmClaim(models.Model):
    _name = "crm.claim"
    _description = "Claim"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "priority,date desc"

    @api.multi
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        team_id = self.env['crm.team'].sudo()._get_default_team_id()
        return self._stage_find(team_id=team_id.id, domain=[('sequence', '=', '1')])

    # id = fields.Integer('ID', readonly=True)
    name = fields.Char('Claim Subject', required=True)
    active = fields.Boolean('Active',default=lambda *a: 1)
    action_next = fields.Char('Next Action')
    date_action_next = fields.Datetime('Next Action Date')
    description = fields.Text('Description')
    resolution = fields.Text('Resolution')
    create_date = fields.Datetime('Creation Date' , readonly=True)
    write_date = fields.Datetime('Update Date' , readonly=True)
    date_deadline = fields.Datetime('Deadline')
    date_closed = fields.Datetime('Closed', readonly=True)
    date = fields.Datetime('Claim Date', select=True,default=lambda self: self._context.get('date', fields.Datetime.now()))
    categ_id = fields.Many2one('crm.claim.category', 'Category')
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], 'Priority', default='1')
    type_action = fields.Selection([('correction', 'Corrective Action'), ('prevention', 'Preventive Action')], 'Action Type')
    user_id = fields.Many2one('res.users', 'Responsible', track_visibility='always', default=lambda self: self.env['res.users'].browse(self._context['uid']))
    user_fault = fields.Char('Trouble Responsible')
    team_id = fields.Many2one('crm.team', 'Sales Team', oldname='section_id', select=True, help="Responsible sales team." \
                                " Define Responsible user and Email account for" \
                                " mail gateway.")  # ,default=lambda self: self.env['crm.team']._get_default_team_id()
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('crm.case'))
    partner_id = fields.Many2one('res.partner', 'Partner')
    email_cc = fields.Text('Watchers Emails', size=252, help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    email_from = fields.Char('Email', size=128, help="Destination email for email gateway.")
    partner_phone = fields.Char(related='partner_id.phone', string='Phone')
    partner_mobile = fields.Char(related='partner_id.mobile', string='Mobile')
    partner_email = fields.Char(related='partner_id.email', string='Email')
    stage_id = fields.Many2one ('crm.claim.stage', 'Stage', track_visibility='onchange',
                domain="['|', ('team_ids', '=', team_id), ('case_default', '=', True)]", default=1)    #,default=lambda self:self.env['crm.claim']._get_default_stage_id()
    cause = fields.Text('Root Cause')
    source_id = fields.Many2one('crm.claim.source', 'Source')
    product_id = fields.Many2one('product.product', 'Bien')
    project_id = fields.Many2one(related='product_id.project_id', string='Projet')
    bloc = fields.Char(related='product_id.bloc', string='Bloc')
    state = fields.Selection([('valid', 'Valide'),
                              ('cancel', 'Annulée'), ], string='Etat', default='valid', track_visibility='onchange')

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self, email=False):
        if not self.partner_id:
            return {'value': {'email_from': False, 'partner_phone': False}}
        address = self.pool.get('res.partner').browse(self.partner_id)
        return {'value': {'email_from': address.email, 'partner_phone': address.phone}}

    @api.model
    def create(self, vals):
        context = dict(self._context or {})
        if vals.get('team_id') and not self._context.get('default_team_id'):
            context['default_team_id'] = vals.get('team_id')

        # context: no_log, because subtype already handle this
        return super(CrmClaim, self).create(vals)

    @api.multi
    def message_new(self,msg, custom_values=None):
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
        defaults = {
            'name': msg.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'partner_id': msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(CrmClaim, self).message_new(msg, custom_values=defaults)

    @api.multi
    def unlink(self):
        raise UserError(_('Suppression non autorisée ! '))

    @api.one
    def action_cancel(self):
        self.state = 'cancel'


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.multi
    def _claim_count(self):
        for claim in self:
            claim_ids = self.env['crm.claim'].search([('partner_id','=',claim.id)])
            claim.claim_count = len(claim_ids)
            
    @api.multi
    def claim_button(self):
        self.ensure_one()
        return {
            'name': 'Partner Claim',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'crm.claim',
            'domain': [('partner_id', '=', self.id)],
        }
        
    claim_count = fields.Integer(string='# Claims',compute='_claim_count')


class CrmClaimCategory(models.Model):
    _name = "crm.claim.category"
    _description = "Category of claim"

    name = fields.Char('Name', required=True, translate=True)
    team_id = fields.Many2one('crm.team', 'Sales Team')


class CrmClaimSource(models.Model):
    _name = "crm.claim.source"
    _description = "Source of claim"

    name = fields.Char('Source', required=True, translate=True)
