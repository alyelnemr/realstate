# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from collections import namedtuple


class SalesTarget(models.Model):
    _name = 'sales.target'
    _inherit = ['mail.thread']
    name = fields.Char(string="Schema", required=True)
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date to", required=True)
    employee_ids = fields.Many2many('hr.employee', string="Employees", relation="sales_target_employees_rel",
                                    required=True)
    # job_id = fields.Many2one('hr.job', string="Job Position", related='employee_id.job_id', readonly=1)
    # user_ids = fields.Many2many('res.users', relation="sales_target_rel", string="Sales Persons", required=True)
    commission_ids = fields.One2many('sales.target.commission', 'sale_target_id', string="Commission")
    target_amount = fields.Float(string="Target Amount")
    # achievement_amount = fields.Float(string="Achievement amount")
    # achievement_percentage = fields.Float(string="Achievement Percentage", compute='compute_achievement_percentage')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
    ], 'State', index=True, default="draft", tracking=True)

    # @api.depends('target_amount', 'achievement_amount')
    # def compute_achievement_percentage(self):
    #     for rec in self:
    #         if rec.target_amount > 0.0:
    #             rec.achievement_percentage = (rec.achievement_amount / rec.target_amount) * 100
    #         else:
    #             rec.achievement_percentage = 0.0

    def check_intersection(self):
        Range = namedtuple('Range', ['start', 'end'])
        previous_policies = self.search([('id', '!=', self.id),
                                         ('state', '=', 'active'),
                                         ('employee_ids', '=', self.employee_ids.ids)])
        if previous_policies:
            for policy in previous_policies:
                r1 = Range(start=policy.date_from, end=policy.date_to)
                r2 = Range(start=self.date_from, end=self.date_to)
                latest_start = max(r1.start, r2.start)
                earliest_end = min(r1.end, r2.end)
                delta = (earliest_end - latest_start).days + 1
                overlap = max(0, delta)
                if overlap:
                    return True
        return False

    def set_active(self):
        self.ensure_one()
        if not self.commission_ids:
            raise ValidationError(_('You Should add commission lines'))
        if self.check_intersection():
            raise ValidationError(_('The same Sales Person have active target in the same period'))
        self.write({
            'state': 'active'
        })

    def set_to_draft(self):
        self.ensure_one()
        self.write({
            'state': 'draft'
        })

    def unlink(self):
        if any(self.filtered(lambda target: target.state not in ('draft'))):
            raise ValidationError(_('You cannot delete active target'))
        return super(SalesTarget, self).unlink()
