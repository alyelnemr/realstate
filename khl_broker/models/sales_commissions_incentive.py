# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SalesCommissionsAndIncentives(models.Model):
    _name = 'sales.commissions.incentives'
    _rec_name = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    job_id = fields.Many2one('hr.job', string="Job Position")
    unit_amount = fields.Float(string="Amount")
    commission_percentage = fields.Float(string="Commission Percentage")
    commission_amount = fields.Float(string="Commission Amount")
    incentive_value = fields.Float(string="Incentive Value")
    bouns_value = fields.Float(string="Bouns Value")
    broker_request_id = fields.Many2many('broker.request', relation="commissions_broker_request_rel",
                                         string="Contracts")
    contract_no = fields.Char(related='broker_request_id.name', readonly=1)
    due_date = fields.Date(string="Due Date")
    make_payroll = fields.Boolean(string="Make Payroll")
    paid = fields.Selection(string="Paying Type",
                            selection=[('not_payed', 'Not Paid'), ('partial', 'Partial Paid'), ('full', 'Fully Paid')],
                            compute='calc_paid')
    unit_id = fields.Many2one('broker.units', string="Unit")
    to_pay_amount = fields.Float(string="To Pay")
    paid_amount = fields.Float(string="Paid")
    remaing_amount = fields.Float(string="Remaining", compute='calc_remaing_amount')
    type = fields.Selection(string="Type",
                            selection=[('incentive', 'Incentive'), ('commission', 'Commission'), ('bouns', 'Bouns')])
    notes = fields.Char(string="Notes")

    def view_commission_details(self):
        view_id = self.env.ref('khl_broker.view_commission_details_view_tree').id
        return {
            'name': 'Commission Details',
            'type': 'ir.actions.act_window',
            'res_model': 'contract.commissions.details',
            'view_id': view_id,
            'view_mode': 'tree',
            'target': 'current',
            'domain': [('broker_request_id', 'in', self.broker_request_id.ids),
                       ('employee_id', '=', self.employee_id.id)]
        }

    @api.constrains('to_pay_amount', 'bouns_value', 'commission_amount', 'incentive_value', 'paid_amount')
    def check_to_pay(self):
        for rec in self:
            total_value = rec.to_pay_amount + rec.paid_amount
            if rec.bouns_value > 0:
                if total_value > rec.bouns_value:
                    raise ValidationError(_('To pay amount + paid amount should be less than bouns value'))
            elif rec.commission_amount > 0:
                if total_value > rec.commission_amount:
                    raise ValidationError(_('To pay amount + paid amount should be less than Commission value'))
            elif rec.incentive_value > 0:
                if total_value > rec.incentive_value:
                    raise ValidationError(_('To pay amount + paid amount should be less than Incentive value'))

    @api.depends('paid_amount', 'bouns_value', 'commission_amount', 'incentive_value')
    def calc_remaing_amount(self):
        for rec in self:
            if rec.bouns_value > 0:
                rec.remaing_amount = rec.bouns_value - rec.paid_amount
            elif rec.commission_amount > 0:
                rec.remaing_amount = rec.commission_amount - rec.paid_amount
            elif rec.incentive_value > 0:
                rec.remaing_amount = rec.incentive_value - rec.paid_amount
            else:
                rec.remaing_amount = 0

    @api.depends('remaing_amount', 'bouns_value', 'commission_amount', 'incentive_value')
    def calc_paid(self):
        for rec in self:
            if rec.bouns_value > 0:
                if rec.paid_amount == 0:
                    rec.paid = 'not_payed'
                else:
                    if rec.bouns_value == rec.paid_amount:
                        rec.paid = 'full'
                    else:
                        rec.paid = 'partial'
            elif rec.commission_amount > 0:
                if rec.paid_amount == 0:
                    rec.paid = 'not_payed'
                else:
                    if rec.commission_amount == rec.paid_amount:
                        rec.paid = 'full'
                    else:
                        rec.paid = 'partial'
            elif rec.incentive_value > 0:
                if rec.paid_amount == 0:
                    rec.paid = 'not_payed'
                else:
                    if rec.incentive_value == rec.paid_amount:
                        rec.paid = 'full'
                    else:
                        rec.paid = 'partial'
            else:
                rec.paid = 'not_payed'
