# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    alias_name = fields.Char(strimg="Alias Name", default='اسماء محمد يونس وشريكها')
    st = fields.Char(string="Commercial Record")
    md = fields.Char(string="MD")
