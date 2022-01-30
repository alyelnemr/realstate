# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BounsSetup(models.Model):
    _name = 'bouns.setup'
    _rec_name = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(string="Name", required=True)
    employee_ids = fields.Many2many('hr.employee', string="Employees", relation="bouns_setup_employees_rel",
                                    required=True)
    amount = fields.Float(string="For Amount", required=True)
    actual_amount = fields.Float(string="Actual Amount", required=True)
