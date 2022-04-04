# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractCommissionDetails(models.Model):
    _name = 'contract.commissions.details'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    job_id = fields.Many2one('hr.job', string="Job Position")
    unit_amount = fields.Float(string="Amount")
    commission_percentage = fields.Float(string="Commission Percentage")
    commission_amount = fields.Float(string="Commission Amount")
    broker_request_id = fields.Many2one('broker.request', string="Broker Request")
    contract_no = fields.Char(related='broker_request_id.name', readonly=1)
    due_date = fields.Date(string="Due Date")
    unit_id = fields.Many2one('broker.units', string="Unit")

