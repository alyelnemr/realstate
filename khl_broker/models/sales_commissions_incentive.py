# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


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
    broker_request_id = fields.Many2one('broker.request', string="Broker Request")
    due_date = fields.Date(string="Due Date")
    make_payroll = fields.Boolean(string="Make Payroll")
    is_paid = fields.Boolean(string="Paid")
    unit_id = fields.Many2one('broker.units', string="Unit")
    paid_amount = fields.Float(string="Paid Amount")
    remaing_amount = fields.Float(string="Remaining Amount")
    type = fields.Selection(string="Type",
                            selection=[('incentive', 'Incentive'), ('commission', 'Commission'), ('bouns', 'Bouns')])
