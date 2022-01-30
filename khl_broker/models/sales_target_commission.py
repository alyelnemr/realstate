# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class SalesTargetCommission(models.Model):
    _name = 'sales.target.commission'
    sale_target_id = fields.Many2one('sales.target', string="Target")
    from_amount = fields.Float(string="From Amount")
    to_amount = fields.Float(string="To Amount")
    commission_percentage = fields.Float(string="Commission Percentage")
