# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from collections import namedtuple


class EmployeesSalesTarget(models.Model):
    _name = 'emp.sales.target'
    _inherit = ['mail.thread']
    name = fields.Char(string="Period", required=True)
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date to", required=True)
    target_line_ids = fields.One2many('emp.sales.target.lines', 'emp_sales_target_id', string="Employees",
                                      required=False, )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
    ], 'State', index=True, default="draft", tracking=True)

    def check_intersection(self):
        Range = namedtuple('Range', ['start', 'end'])
        previous_policies = self.env['emp.sales.target.lines'].search([('emp_sales_target_id', '!=', self.id),
                                                                       ('emp_sales_target_id.state', '=', 'active'),
                                                                       ('employee_id', 'in',
                                                                        self.target_line_ids.mapped(
                                                                            'employee_id').ids)])
        if previous_policies:
            for policy in previous_policies:
                r1 = Range(start=policy.emp_sales_target_id.date_from, end=policy.emp_sales_target_id.date_to)
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
        if not self.target_line_ids:
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
        return super(EmployeesSalesTarget, self).unlink()
