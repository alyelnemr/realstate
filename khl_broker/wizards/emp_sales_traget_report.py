from datetime import date

from odoo import models, fields, api, _


class EmpSalesTargetReport(models.TransientModel):
    _name = 'emp.sales.target.report'
    _description = 'Emp Sales Target Report'

    period_ids = fields.Many2many('emp.sales.target', relation="emp_sales_target_rel", string="Targets")
    employee_ids = fields.Many2many('hr.employee', relation="employees_sales_target_rel", string="Employees")
    period_employee_ids = fields.Many2many('hr.employee', compute='compute_period_employee',
                                           relation="employees_period_sales_target_rel", string="Employees")

    def print(self):
        return self.env.ref('khl_broker.emp_sales_target_report_id').report_action(self.id)

    @api.depends('period_ids')
    def compute_period_employee(self):
        for rec in self:
            if rec.period_ids:
                employees = self.period_ids.mapped('target_line_ids').mapped('employee_id')
                rec.period_employee_ids = [(6, 0, employees.ids)]
            else:
                rec.period_employee_ids = False
