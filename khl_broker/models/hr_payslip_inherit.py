# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_all_commissions_request(self):
        commission_request = self.env['sales.commissions.incentives'].search([('employee_id', '=', self.employee_id.id),
                                                                              ('due_date', '>=', self.date_from),
                                                                              ('due_date', '<=', self.date_to),
                                                                              ('type', '=', 'commission'),
                                                                              ('make_payroll', '=', True)])
        return commission_request

    @api.model
    def get_all_bouns_request(self):
        commission_request = self.env['sales.commissions.incentives'].search([('employee_id', '=', self.employee_id.id),
                                                                              ('due_date', '>=', self.date_from),
                                                                              ('due_date', '<=', self.date_to),
                                                                              ('type', '=', 'bouns'),
                                                                              ('make_payroll', '=', True)])
        return commission_request

    commission_amount = fields.Float(string="Commission Amount", compute='compute_commission_amount')
    bouns_amount = fields.Float(string="Bouns amount", compute='compute_commission_amount')

    @api.depends('employee_id', 'date_from', 'date_to')
    def compute_commission_amount(self):
        for rec in self:
            rec.commission_amount = sum(self.get_all_commissions_request().mapped('commission_amount'))
            rec.bouns_amount = sum(self.get_all_bouns_request().mapped('bouns_value'))

    def action_payslip_paid(self):
        res = super(HrPayslipInherit, self).action_payslip_done()
        commissions_objs = self.get_all_commissions_request()
        bouns_objs = self.get_all_bouns_request()
        commissions_objs.write({'is_paid': True})
        bouns_objs.write({'is_paid': True})
        return res
