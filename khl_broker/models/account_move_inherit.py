# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import math


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    developer_company = fields.Many2one('res.partner', string="Developer Company")
    unit_id = fields.Many2one('broker.units', string="Unit")

    def get_detailed_taxes(self):
        taxes = {}
        for line in self.invoice_line_ids:
            if line.tax_ids:
                for tax in line.tax_ids:
                    if tax.name not in taxes.keys():
                        taxes[tax.name] = (tax.amount / 100) * line.price_subtotal
        return taxes

    def get_amount_in_ar(self, amount):
        for rec in self:
            if rec.currency_id:
                txt = self.currency_id.with_context(lang='ar_SY').amount_to_text(amount)
                return txt.replace("and", "و")
            else:
                return ''

    def return_value_details(self, amount):
        if amount:
            frac, whole = math.modf(amount)
            return frac
