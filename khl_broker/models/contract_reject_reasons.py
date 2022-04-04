# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ContractRejectReasons(models.Model):
    _name = 'contract.reject.reasons'

    reject_reason_id = fields.Many2one('broker.request', string="Broker", ondelete="cascade")
    user_id = fields.Many2one('res.users', string="User")
    date = fields.Datetime(string="Date")
    reason = fields.Text(string="Reason")
