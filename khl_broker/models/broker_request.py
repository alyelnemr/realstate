# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import api, fields, models, tools, _
import logging
import base64
from itertools import groupby
from operator import itemgetter


class BrokerRequest(models.Model):
    _name = 'broker.request'
    _rec_name = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", readonly=1, default='New')
    developer_company = fields.Many2one('res.partner', string="Developer Company", required=True, tracking=True)
    customer_id = fields.Many2one('unit.reservation.customer.mobile', string="Customer", required=True, tracking=True)
    unit_id = fields.Many2one('broker.units', string="Unit", required=True, tracking=True)
    unit_name = fields.Char(string="Unit Name", related='unit_id.name', readonly=True)
    unit_code = fields.Char(string="Unit Code", related='unit_id.code', readonly=True)
    project_id = fields.Many2one('unit.projects', string="Project Name", related='unit_id.project_id', readonly=True)
    price = fields.Float(string="Price", related='unit_id.price', readonly=True)
    developer_percentage = fields.Float(string="Developer Percentage", related='unit_id.commission_percentage',
                                        readonly=1)
    state = fields.Selection(related='unit_id.state', readonly=True)
    # payment_state = fields.Selection(string="Payment State", selection=[('partially_collected', 'Partially Collected'),
    #                                                                     ('fully_collected', 'Fully Collected')])
    company_commission = fields.Float(string="Company Commission", related='unit_id.commission')
    contract_date = fields.Date(string="Contract Date")
    reserve_date = fields.Date(string="Reserve Date")
    pre_contract_reservation_id = fields.Many2one('unit.pre.contract', string="Unit Reservation")
    user_ids = fields.One2many('broker.request.users', 'broker_request_id', string="Sales Persons")
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    account_move_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    company_amount_after_developer_percentage = fields.Float(string="Company Commission After Developer Percentage",
                                                             compute='compute_company_amount_after_developer_percentage')
    before_tax_value = fields.Float(string="Before Tax", compute='compute_before_tax')
    internal_taxes_percentage = fields.Float(string="Internal Taxes Percentage", default=14)
    company_amount_after_internal_taxes = fields.Float(string="Company Commission After Internal Taxes",
                                                       compute='compute_company_amount_after_internal_taxes')
    with_holding = fields.Float(string="WithHolding %", default=5)
    with_holding_value = fields.Float(string="WithHolding Value", compute='compute_with_holding_value')
    net_value = fields.Float(string="Net Value", compute='compute_net_value')
    sales_man_commission_based_value = fields.Float(string="Sales Man Commission Based Value",
                                                    compute='compute_sales_man_commission_based_value')
    sales_person_incentive_type = fields.Selection(string="Incentive Sales Person Type",
                                                   selection=[('percentage', 'Percentage'),
                                                              ('value', 'Value')])
    sales_manager_incentive_type = fields.Selection(string="Incentive Sales Manager Type",
                                                    selection=[('percentage', 'Percentage'),
                                                               ('value', 'Value')])
    incentive_sales_person_percentage = fields.Float(string="Incentive sales person Percentage %")
    incentive_sales_manager_percentage = fields.Float(string="Incentive sales Manager Percentage %")
    incentive_sales_person_value = fields.Float(string="Incentive sales person Value")
    incentive_sales_manager_value = fields.Float(string="Incentive sales Manager Value")
    intensive_value = fields.Float(string="Incentive Value")
    space = fields.Float(string="Area", related='unit_id.space', readonly=1)
    floor = fields.Integer(string="Floor", related='unit_id.floor', readonly=1)
    incentive_value = fields.Float(string="incentive Value")
    currency_id = fields.Many2one('res.currency', string='Currency', help="Currency",
                                  default=lambda self: self.env.user.company_id.currency_id)
    reject_reasons_ids = fields.One2many('contract.reject.reasons', inverse_name="reject_reason_id",
                                         string="Reject Reasons")
    other_deductions = fields.Float(string="Other Deductions %", default=2)
    tax_type = fields.Selection(string="Tax Type", selection=[('1', '/'), ('2', '*'), ], required=True, default='1')

    def _compute_amount_text(self, amount):
        for rec in self:
            if rec.currency_id:
                txt = self.currency_id.with_context(lang='ar_SY').amount_to_text(amount)
                return txt.replace("and", "و")
            else:
                return ''

    def get_contract_reviewrs(self):
        return self.env['contract.reviewers'].search([]).mapped('employee_ids')

    def approve(self):
        self.ensure_one()
        code_reviewrs = self.get_contract_reviewrs()
        if code_reviewrs:
            if self.env.user.id not in code_reviewrs.mapped('user_id').ids:
                raise ValidationError('Only Contract Reviewers Can Approve.')
            else:
                self.unit_id.state = 'approved'
        else:
            raise ValidationError('There Is No Contract Reviewers')

    def reject(self):
        self.ensure_one()
        code_reviewrs = self.get_contract_reviewrs()
        if code_reviewrs:
            if self.env.user.id not in code_reviewrs.mapped('user_id').ids:
                raise ValidationError('Only Contract Reviewers Can Reject.')
            else:
                wizard_form = self.env.ref('khl_broker.view_contract_reject_reason_wizard')
                new_context = self.env.context.copy()
                new_context.update({
                    'default_broker_request_id': self.id,
                })
                return {
                    'name': 'Contract Reject',
                    'type': 'ir.actions.act_window',
                    'res_model': 'contract.reject.reason',
                    'view_id': wizard_form.id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': new_context,
                }
        else:
            raise ValidationError('There Is No Contract Reviewers')

    @api.depends('company_commission', 'internal_taxes_percentage', 'tax_type')
    def compute_before_tax(self):
        for rec in self:
            if rec.internal_taxes_percentage:
                if rec.tax_type == '1':
                    perc = 1 + (rec.internal_taxes_percentage / 100)
                    rec.before_tax_value = rec.company_commission / perc
                else:
                    rec.before_tax_value = rec.company_commission
            else:
                rec.before_tax_value = rec.company_commission

    @api.depends('with_holding', 'before_tax_value')
    def compute_with_holding_value(self):
        for rec in self:
            if rec.with_holding:
                rec.with_holding_value = rec.before_tax_value * (rec.with_holding / 100)
            else:
                rec.with_holding_value = rec.before_tax_value

    @api.depends('with_holding_value', 'before_tax_value', 'company_amount_after_internal_taxes')
    def compute_net_value(self):
        for rec in self:
            rec.net_value = (rec.company_amount_after_internal_taxes + rec.before_tax_value) - rec.with_holding_value

    @api.depends('before_tax_value', 'with_holding_value', 'other_deductions')
    def compute_sales_man_commission_based_value(self):
        for rec in self:
            rec.sales_man_commission_based_value = rec.before_tax_value - rec.with_holding_value
            if rec.other_deductions:
                rec.sales_man_commission_based_value = rec.sales_man_commission_based_value - (
                        rec.sales_man_commission_based_value * (rec.other_deductions / 100))

    @api.onchange('pre_contract_reservation_id')
    def onchange_pre_contract_reservation_id(self):
        if self.pre_contract_reservation_id:
            employees = []
            self.developer_company = self.pre_contract_reservation_id.partner_id.id
            self.unit_id = self.pre_contract_reservation_id.unit_id.id
            self.reserve_date = self.pre_contract_reservation_id.reservation_date
            self.customer_id = self.env['unit.reservation.customer.mobile'].search(
                [('mobile_no', '=', self.pre_contract_reservation_id.mobile_no)], limit=1).id
            if self.pre_contract_reservation_id.employee_ids:
                for employee in self.pre_contract_reservation_id.employee_ids:
                    employees.append((0, 0, {
                        'employee_id': employee.id
                    }))
            self.user_ids = employees
        else:
            self.developer_company = False
            self.unit_id = False
            self.reserve_date = False
            self.customer_id = False
            self.user_ids = False

    @api.depends('company_commission', 'developer_percentage')
    def compute_company_amount_after_developer_percentage(self):
        for rec in self:
            if rec.developer_percentage:
                developer_amount = rec.company_commission * (rec.developer_percentage / 100)
                rec.company_amount_after_developer_percentage = rec.company_commission - developer_amount
            else:
                rec.company_amount_after_developer_percentage = rec.company_commission

    @api.depends('internal_taxes_percentage', 'before_tax_value')
    def compute_company_amount_after_internal_taxes(self):
        for rec in self:
            if rec.internal_taxes_percentage:
                rec.company_amount_after_internal_taxes = rec.before_tax_value * (
                        rec.internal_taxes_percentage / 100)
            else:
                rec.company_amount_after_internal_taxes = 0.0

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['unit_code'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('broker.request') or _('New')
        return super(BrokerRequest, self).create(vals)

    def reserve_unit(self):
        self.ensure_one()
        self.unit_id.write({
            'state': 'reserved'
        })

    def un_reserve_unit(self):
        self.ensure_one()
        self.unit_id.write({
            'state': 'valid'
        })

    def sell_unit(self):
        # self.ensure_one()
        # company = self.env.user.company_id
        # template = self.env.ref('khl_broker.contract_notification_template')
        # report = self.env.ref('khl_broker.contract_report_id')._render_qweb_pdf(self.id)
        # filename = self.name + '.pdf'
        # contract = self.env['ir.attachment'].create({
        #     'name': filename,
        #     'type': 'binary',
        #     'datas': base64.b64encode(report[0]),
        #     'store_fname': filename,
        #     'res_model': 'broker.request',
        #     'res_id': self.id,
        #     'mimetype': 'application/x-pdf'
        # })
        # if contract_reviewers and contract_reviewers.employee_ids:
        #     for employee in contract_reviewers.employee_ids:
        #         template_values = {
        #             'email_from': company.partner_id.email,
        #             'email_to': employee.work_email,
        #             'attachment_ids': [(6, 0, [contract.id])]
        #         }
        #         template.write(template_values)
        #         template.with_context(send_to_user=employee.name).send_mail(self.id, force_send=True)
        self.unit_id.write({
            'state': 'sold'
        })

    def un_sell_unit(self):
        self.ensure_one()
        self.unit_id.write({
            'state': 'valid'
        })

    def update_achieved_amount(self):
        for rec in self:
            current_target = self.env['emp.sales.target'].search([('state', '=', 'active'),
                                                                  ('date_from', '<=', rec.contract_date),
                                                                  ('date_to', '>=', rec.contract_date)], limit=1)
            if current_target:
                for target in current_target.target_line_ids:
                    if target.employee_id in rec.user_ids.mapped('employee_id'):
                        target.achieved_amount = target.achieved_amount + rec.price

    def commission_request(self):
        self.ensure_one()
        wizard_form = self.env.ref('khl_broker.view_commission_request_report_wizard')
        new_context = self.env.context.copy()
        new_context.update({
            'default_broker_request_id': self.id,
        })
        return {
            'name': 'Commission And Incentives  Report',
            'type': 'ir.actions.act_window',
            'res_model': 'commission.request.report',
            'view_id': wizard_form.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': new_context,
        }

    def get_sales_person_incentive_value(self):
        self.ensure_one()
        sale_person_incentive_value = 0.0
        if self.user_ids:
            if self.sales_person_incentive_type == 'percentage' and self.incentive_sales_person_percentage > 0:
                sale_person_incentive_value = (self.price * (self.incentive_sales_person_percentage / 100)) / len(
                    self.user_ids)
            if self.sales_person_incentive_type == 'value' and self.incentive_sales_person_value > 0:
                sale_person_incentive_value = (self.incentive_sales_person_value) / len(self.user_ids)

        return sale_person_incentive_value

    def get_sales_manager_incentive_value(self):
        self.ensure_one()
        sales_manager_incentive_value = 0.0
        for employee in self.user_ids:
            if self.sales_manager_incentive_type == 'percentage' and self.incentive_sales_manager_percentage > 0 and employee.employee_id.parent_id:
                sales_manager_incentive_value = (self.price * (self.incentive_sales_manager_percentage / 100)) / len(
                    self.user_ids)
            if self.sales_manager_incentive_type == 'value' and self.incentive_sales_manager_value > 0 and employee.employee_id.parent_id:
                sales_manager_incentive_value = (self.incentive_sales_manager_value) / len(self.user_ids)
        return sales_manager_incentive_value

    def create_invoice(self):
        # create product of type service
        self.ensure_one()
        journal = self.env['account.move'].with_context(default_move_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(
                _('Please define an accounting sales journal for the company %s (%s).', self.company_id.name,
                  self.company_id.id))
        product = self.env['product.product'].sudo().create({
            'name': self.unit_id.name,
            'type': 'service'
        })
        move = self.env['account.move'].sudo().create([{
            'move_type': 'out_invoice',
            'journal_id': journal.id,
            'contract_id': self.id,
            'partner_id': self.developer_company.id,
            'date': fields.Date.today(),
            'invoice_date': fields.Date.today(),
            'company_id': self.company_id.id,
            'invoice_line_ids': [(0, 0, {'product_id': product.id,
                                         'price_unit': self.before_tax_value,
                                         'account_id': product.categ_id.property_account_income_categ_id.id,
                                         'analytic_account_id': self.analytic_account_id.id})]
        }])
        self.unit_id.write({
            'state': 'invoiced'
        })
        self.account_move_id = move.id
        # self.get_sales_target_for_user()
        self.update_achieved_amount()
        # self.get_employee_bouns_value()
        # if self.pre_contract_reservation_id:
        #     self.pre_contract_reservation_id.write({
        #         'state': 'contract'
        #     })

    def calculate_commission(self):
        self.get_sales_target_for_user()

    def calculate_bouns(self):
        self.get_employee_bouns_value()

    def get_employee_bouns_value(self):
        for rec in self:
            prev_recs = self.env['sales.commissions.incentives'].search(
                [('broker_request_id', '=', rec.id),
                 ('type', '=', 'bouns'), '|',
                 ('make_payroll', '=', False),
                 ('paid', '=', 'not_payed')])
            if prev_recs:
                prev_recs.unlink()
            if rec.user_ids:
                vals = []
                price = rec.price / len(rec.user_ids)
                for user in rec.user_ids:
                    if user.employee_id.coach_id:
                        couch_bouns = self.env['bouns.setup'].search(
                            [('employee_ids', '=', user.employee_id.coach_id.id)], limit=1)
                        sales_manger_bouns = self.env['bouns.setup'].search(
                            [('employee_ids', '=', user.employee_id.parent_id.id)], limit=1)
                        if couch_bouns:
                            vals.append({
                                'employee_id': user.employee_id.coach_id.id,
                                'unit_id': rec.unit_id.id,
                                'job_id': user.employee_id.coach_id.job_id.id,
                                'broker_request_id': rec.id,
                                'bouns_value': (couch_bouns.amount / couch_bouns.actual_amount) * price,
                                'due_date': datetime.now().date() + relativedelta(months=1),
                                'name': 'Bouns Value',
                                'type': 'bouns'
                            })
                        if sales_manger_bouns:
                            vals.append({
                                'employee_id': user.employee_id.parent_id.id,
                                'unit_id': rec.unit_id.id,
                                'job_id': user.employee_id.parent_id.job_id.id,
                                'broker_request_id': rec.id,
                                'bouns_value': (sales_manger_bouns.amount / sales_manger_bouns.actual_amount) * price,
                                'due_date': datetime.now().date() + relativedelta(months=1),
                                'name': 'Bouns Value',
                                'type': 'bouns'
                            })
                self.env['sales.commissions.incentives'].create(vals)

    def get_sales_target_for_user(self):
        active_ids = self._context.get('active_ids')
        contract_ids = self.browse(active_ids)
        sales_person_args = ["employee_id"]
        team_lead_args = ["coach_id"]
        sales_manager_args = ["parent_id"]
        sales_person_grouper = itemgetter(*sales_person_args)
        team_lead_grouper = itemgetter(*team_lead_args)
        sales_manager_grouper = itemgetter(*sales_manager_args)
        now = datetime.now()
        today = now.date()
        contract_ids = contract_ids.filtered(
            lambda x: x.account_move_id != False and x.account_move_id.payment_state == 'paid')
        grouped_sales_persons_emps = {k: list(v) for k, v in groupby(
            sorted(contract_ids.mapped('user_ids'), key=sales_person_grouper), sales_person_grouper)}
        grouped_team_lead_emps = {k: list(v) for k, v in groupby(
            sorted(contract_ids.mapped('user_ids'), key=team_lead_grouper), team_lead_grouper)}
        grouped_coach_emps = {k: list(v) for k, v in groupby(
            sorted(contract_ids.mapped('user_ids'), key=sales_manager_grouper), sales_manager_grouper)}
        vals = []
        details_vals = []
        prev_records = self.env['sales.commissions.incentives'].search([('broker_request_id', '=', contract_ids.ids),
                                                                        ('paid', '=', 'not_payed')])
        prev_records_details = self.env['contract.commissions.details'].search([('broker_request_id', 'in', contract_ids.ids)])
        if prev_records:
            prev_records.unlink()
        if prev_records_details:
            prev_records_details.unlink()
        for k, v in grouped_sales_persons_emps.items():
            if v:
                employee_value = sum(emp.broker_request_id.sales_man_commission_based_value for emp in v) / len(k)
                company_commission = sum(emp.broker_request_id.company_commission for emp in v)
                user_target = self.env['sales.target'].search([('employee_ids', '=', k.id),
                                                               ('date_from', '<=', today),
                                                               ('date_to', '>=', today),
                                                               ('state', '=', 'active')], limit=1)
                for line in user_target.commission_ids:
                    if company_commission and line.from_amount <= company_commission < line.to_amount:
                        vals.append({
                            'employee_id': k.id,
                            'job_id': k.job_id.id,
                            'unit_amount': employee_value,
                            'commission_percentage': line.commission_percentage,
                            'commission_amount': (
                                                         line.commission_percentage / 100) * employee_value,
                            'broker_request_id': [(6, 0, [emp.id for emp in v])],
                            'due_date': datetime.now().date() + relativedelta(months=1),
                            'name': 'Commission Value',
                            'type': 'commission'})
        for k, v in grouped_team_lead_emps.items():
            employee_value = sum(emp.broker_request_id.sales_man_commission_based_value for emp in v) / len(k)
            company_commission = sum(emp.broker_request_id.company_commission for emp in v)
            if k:
                team_leader_target = self.env['sales.target'].search(
                    [('employee_ids', '=', k.id),
                     ('date_from', '<=',
                      today),
                     ('date_to', '>=',
                      today),
                     ('state', '=', 'active')], limit=1)
                for line in team_leader_target.commission_ids:
                    if company_commission and line.from_amount <= company_commission < line.to_amount:
                        vals.append({
                            'employee_id': k.id,
                            # 'unit_id': user.broker_request_id.unit_id.id,
                            'job_id': k.job_id.id,
                            'unit_amount': employee_value,
                            'commission_percentage': line.commission_percentage,
                            'commission_amount': (
                                                         line.commission_percentage / 100) * employee_value,
                            'broker_request_id': [(6, 0, [emp.id for emp in v])],
                            'due_date': datetime.now().date() + relativedelta(months=1),
                            'name': 'Commission Value',
                            'type': 'commission'})
        for k, v in grouped_coach_emps.items():
            employee_value = sum(emp.broker_request_id.sales_man_commission_based_value for emp in v) / len(k)
            company_commission = sum(emp.broker_request_id.company_commission for emp in v)
            if k:
                sales_manager_target = self.env['sales.target'].search(
                    [('employee_ids', '=', k.id),
                     ('date_from', '<=',
                      today),
                     ('date_to', '>=',
                      today),
                     ('state', '=', 'active')], limit=1)
                for line in sales_manager_target.commission_ids:
                    if company_commission and line.from_amount <= company_commission < line.to_amount:
                        vals.append({
                            'employee_id': k.id,
                            # 'unit_id': user.broker_request_id.unit_id.id,
                            'job_id': k.job_id.id,
                            'unit_amount': employee_value,
                            'commission_percentage': line.commission_percentage,
                            'commission_amount': (
                                                         line.commission_percentage / 100) * employee_value,
                            'broker_request_id': [(6, 0, [emp.id for emp in v])],
                            'due_date': datetime.now().date() + relativedelta(months=1),
                            'name': 'Commission Value',
                            'type': 'commission'})
        for contract in contract_ids:
            employee_value = contract.sales_man_commission_based_value / len(contract.user_ids)
            company_commission = contract.company_commission
            for user in contract.user_ids:
                user_target = self.env['sales.target'].search([('employee_ids', '=', user.employee_id.id),
                                                               ('date_from', '<=', today),
                                                               ('date_to', '>=', today),
                                                               ('state', '=', 'active')], limit=1)
                for line in user_target.commission_ids:
                    if company_commission and line.from_amount <= company_commission < line.to_amount:
                        details_vals.append({
                            'employee_id': user.employee_id.id,
                            'job_id': user.employee_id.job_id.id,
                            'unit_amount': employee_value,
                            'commission_percentage': line.commission_percentage,
                            'commission_amount': (
                                                         line.commission_percentage / 100) * employee_value,
                            'broker_request_id': contract.id,
                            'due_date': datetime.now().date() + relativedelta(months=1),
                            'name': 'Commission Value'})
                if user.coach_id:
                    user_target = self.env['sales.target'].search([('employee_ids', '=', user.coach_id.id),
                                                                   ('date_from', '<=', today),
                                                                   ('date_to', '>=', today),
                                                                   ('state', '=', 'active')], limit=1)
                    for line in user_target.commission_ids:
                        if company_commission and line.from_amount <= company_commission < line.to_amount:
                            details_vals.append({
                                'employee_id': user.coach_id.id,
                                'job_id': user.coach_id.job_id.id,
                                'unit_amount': employee_value,
                                'commission_percentage': line.commission_percentage,
                                'commission_amount': (
                                                             line.commission_percentage / 100) * employee_value,
                                'broker_request_id': contract.id,
                                'due_date': datetime.now().date() + relativedelta(months=1),
                                'name': 'Commission Value'})
                if user.parent_id:
                    user_target = self.env['sales.target'].search([('employee_ids', '=', user.parent_id.id),
                                                                   ('date_from', '<=', today),
                                                                   ('date_to', '>=', today),
                                                                   ('state', '=', 'active')], limit=1)
                    for line in user_target.commission_ids:
                        if company_commission and line.from_amount <= company_commission < line.to_amount:
                            details_vals.append({
                                'employee_id': user.parent_id.id,
                                'job_id': user.parent_id.job_id.id,
                                'unit_amount': employee_value,
                                'commission_percentage': line.commission_percentage,
                                'commission_amount': (
                                                             line.commission_percentage / 100) * employee_value,
                                'broker_request_id': contract.id,
                                'due_date': datetime.now().date() + relativedelta(months=1),
                                'name': 'Commission Value'})

        self.env['sales.commissions.incentives'].create(vals)
        self.env['contract.commissions.details'].create(details_vals)

    def calculate_incentive(self):
        for rec in self:
            vals = []
            prev_recs = self.env['sales.commissions.incentives'].search(
                [('broker_request_id', '=', rec.id), ('type', '=', 'incentive')])
            if prev_recs:
                prev_recs.unlink()
            for employee in rec.user_ids:
                if rec.sales_person_incentive_type == 'percentage' and rec.incentive_sales_person_percentage > 0:
                    incentive_value = (rec.price * (rec.incentive_sales_person_percentage / 100)) / len(rec.user_ids)
                    vals.append({
                        'employee_id': employee.employee_id.id,
                        'unit_id': rec.unit_id.id,
                        'job_id': employee.employee_id.job_id.id,
                        'incentive_value': incentive_value,
                        'broker_request_id': rec.id,
                        'due_date': datetime.now().date() + relativedelta(months=1),
                        'name': 'Incentive Value',
                        'type': 'incentive'
                    })
                if rec.sales_person_incentive_type == 'value' and rec.incentive_sales_person_value > 0:
                    incentive_value = (rec.incentive_sales_person_value) / len(rec.user_ids)
                    vals.append({
                        'employee_id': employee.employee_id.id,
                        'unit_id': rec.unit_id.id,
                        'job_id': employee.employee_id.job_id.id,
                        'incentive_value': incentive_value,
                        'broker_request_id': rec.id,
                        'due_date': datetime.now().date() + relativedelta(months=1),
                        'name': 'Incentive Value',
                        'type': 'incentive'
                    })
                if rec.sales_manager_incentive_type == 'percentage' and rec.incentive_sales_manager_percentage > 0 and employee.employee_id.parent_id:
                    incentive_value = (rec.price * (rec.incentive_sales_manager_percentage / 100)) / len(rec.user_ids)
                    vals.append({
                        'employee_id': employee.employee_id.parent_id.id,
                        'unit_id': rec.unit_id.id,
                        'job_id': employee.employee_id.parent_id.job_id.id,
                        'incentive_value': incentive_value,
                        'broker_request_id': rec.id,
                        'due_date': datetime.now().date() + relativedelta(months=1),
                        'name': 'Incentive Value',
                        'type': 'incentive'
                    })
                if rec.sales_manager_incentive_type == 'value' and rec.incentive_sales_manager_value > 0 and employee.employee_id.parent_id:
                    incentive_value = (rec.incentive_sales_manager_value) / len(rec.user_ids)
                    vals.append({
                        'employee_id': employee.employee_id.parent_id.id,
                        'unit_id': rec.unit_id.id,
                        'job_id': employee.employee_id.parent_id.job_id.id,
                        'incentive_value': incentive_value,
                        'broker_request_id': rec.id,
                        'due_date': datetime.now().date() + relativedelta(months=1),
                        'name': 'Incentive Value',
                        'type': 'incentive'
                    })
            self.env['sales.commissions.incentives'].create(vals)

    def action_view_invoice(self):
        return {
            'name': _('Unit Reservation Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'move_type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'res_id': self.account_move_id.id,
        }

    @api.model
    def drop_account_constraint(self):
        self.env.cr.execute("""alter table account_move drop constraint IF EXISTS account_move_check_credit_debit""")
        self.env.cr.execute(
            """alter table account_move drop constraint IF EXISTS account_move_check_accountable_required_fields""")
        self.env.cr.execute(
            """alter table account_move drop constraint IF EXISTS account_move_check_non_accountable_fields_null""")
        self.env.cr.execute(
            """alter table account_move drop constraint IF EXISTS account_move_check_amount_currency_balance_sign""")
