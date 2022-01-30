# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    commission_percentage = fields.Float(string="Commission Percentage")

