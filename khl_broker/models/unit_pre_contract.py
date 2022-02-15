# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from collections import namedtuple


class UnitPreContrct(models.Model):
    _name = 'unit.pre.contract'
    _rec_name = 'ref_number'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", readonly=1, default='New')
    ref_number = fields.Char(string="Reservation Number", required=1)
    partner_id = fields.Many2one('res.partner', string="Developer Company")
    project_id = fields.Many2one('unit.projects', string="Project")
    reservation_value = fields.Float(string="Reservation Value")
    reservation_date = fields.Date(string="Reservation Date", default=fields.Date.context_today)
    customer_req = fields.Text(string="Customer Requirements", required=False, )
    mobile_no = fields.Char(string="Customer Mobile Number", required=True)
    address = fields.Char(string="Address")
    customer_name = fields.Char(string="Customer Name")
    is_found = fields.Boolean(string="Found")
    employee_ids = fields.Many2many('hr.employee', relation="unit_pre_contract_employees_rel", string="Sales Persons")
    notes = fields.Text(string="Notes")
    state = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('contract', 'Contract'),
    ], 'State', index=True, default="draft", tracking=True)

    contract_count = fields.Integer(string="Contract Count", compute='compute_contract_count')
    unit_id = fields.Many2one('broker.units', string="Unit")


    @api.depends('state')
    def compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(self.env['broker.request'].search([('pre_contract_reservation_id', '=', rec.id)]))

    def action_view_contracts(self):
        contracts = self.env['broker.request'].search([('pre_contract_reservation_id', '=', self.id)])
        return {
            'name': _('Contract'),
            'domain': [('id', 'in', contracts.ids)],
            'res_model': 'broker.request',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('khl_broker.view_broker_request_tree').id, 'tree'),
                      (self.env.ref('khl_broker.view_broker_request_form').id, 'form')],
        }

    @api.model
    def create(self, vals):
        if not vals.get('unit_code') or vals['unit_code'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('unit.pre.contract') or _('New')
        return super(UnitPreContrct, self).create(vals)

    def confirm(self):
        self.ensure_one()
        mobile_data = self.env['unit.reservation.customer.mobile'].search([('mobile_no', '=', self.mobile_no)], limit=1)
        if mobile_data:
            pass
        else:
            is_found = self.env['unit.reservation.customer.mobile'].search([('mobile_no', '=', self.mobile_no)])
            if is_found:
                raise ValidationError(_('Mobile Number Already Exist !'))
            else:
                self.env['unit.reservation.customer.mobile'].create({
                    'mobile_no': self.mobile_no,
                    'unit_reservation_id': self.id,
                    'customer_name': self.customer_name,
                    'address': self.address
                })
        self.state = 'confirmed'

    @api.onchange('mobile_no')
    def onchange_mobile_date(self):
        if not self.mobile_no:
            self.address = False
            self.customer_name = False

    def check_mobile(self):
        self.ensure_one()
        mobile_data = self.env['unit.reservation.customer.mobile'].search([('mobile_no', '=', self.mobile_no)], limit=1)
        if mobile_data:
            self.is_found = True
            self.customer_name = mobile_data.customer_name
            self.address = mobile_data.address