# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    senior_sales_id = fields.Many2one('hr.employee', string="Senior Sales")
