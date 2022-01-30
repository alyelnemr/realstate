# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MobileData(models.Model):
    _name = 'unit.reservation.customer.mobile'
    _rec_name = 'customer_name'
    _inherit = ['mail.thread']

    mobile_no = fields.Char(string="Mobile No")
    unit_reservation_id = fields.Many2one('unit.pre.contract', string="Unit Reservation")
    customer_name = fields.Char(string="Customer Name")
    address = fields.Char(string="Address")

    @api.constrains('mobile_no')
    def check_mobile_no(self):
        for rec in self:
            previous_data = self.search([('mobile_no', '=', rec.mobile_no), ('id', '!=', rec.id)])
            if previous_data:
                raise ValidationError(_('Mobile Number Already Exist !'))

    contract_count = fields.Integer(string="Contract Count", compute='compute_contract_count')
    reservation_count = fields.Integer(string="Reservation Count", compute='compute_reservation_count')
    unit_id = fields.Many2one('broker.units', string="Unit")

    def compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(self.env['broker.request'].search([('customer_id', '=', rec.id)]))

    def compute_reservation_count(self):
        for rec in self:
            rec.reservation_count = len(self.env['unit.pre.contract'].search([('id', '=', rec.unit_reservation_id.id)]))

    def action_view_contracts(self):
        contracts = self.env['broker.request'].search([('customer_id', '=', self.id)])
        return {
            'name': _('Contract'),
            'domain': [('id', 'in', contracts.ids)],
            'res_model': 'broker.request',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('khl_broker.view_broker_request_tree').id, 'tree'),
                      (self.env.ref('khl_broker.view_broker_request_form').id, 'form')],
        }

    def action_view_reservation(self):
        reservations = self.env['unit.pre.contract'].search([('id', '=', self.unit_reservation_id.id)])
        return {
            'name': _('Reservations'),
            'domain': [('id', 'in', reservations.ids)],
            'res_model': 'unit.pre.contract',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('khl_broker.view_unit_pre_contract_tree').id, 'tree'),
                      (self.env.ref('khl_broker.view_units_pre_contract_form').id, 'form')],
        }
