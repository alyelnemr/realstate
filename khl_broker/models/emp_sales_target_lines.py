# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class EmpSalesTargetLines(models.Model):
    _name = 'emp.sales.target.lines'
    emp_sales_target_id = fields.Many2one('emp.sales.target', string="Target")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    target_amount = fields.Float(string="Target Amount")
    achieved_amount = fields.Float(string="Achieved Amount")
    remaining_amount = fields.Float(string="Remaining Amount", compute='compute_remaining_amount')
    achieved_percentage = fields.Float(string="Achieved %", compute='compute_achievement_percentage')

    @api.depends('target_amount', 'achieved_amount')
    def compute_achievement_percentage(self):
        for rec in self:
            if rec.target_amount > 0.0:
                rec.achieved_percentage = (rec.achieved_amount / rec.target_amount) * 100
            else:
                rec.achieved_percentage = 0.0

    @api.depends('target_amount', 'achieved_amount')
    def compute_remaining_amount(self):
        for rec in self:
            rec.remaining_amount = rec.target_amount - rec.achieved_amount
