# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

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
