# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class UnitProjects(models.Model):
    _name = 'unit.projects'
    _rec_name = 'name'
    name = fields.Char(string="Name", required=True)
