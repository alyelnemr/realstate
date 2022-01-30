# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BrokerTeams(models.Model):
    _name = 'broker.teams'
    _rec_name = 'name'
    _inherit = ['mail.thread']

    name = fields.Char(string="Team Name", required=True)
    sales_manger_id = fields.Many2one('hr.employee', string="Sales Manager", required=True)
    team_leader_id = fields.Many2one('hr.employee', string="Team Leader", required=True)
    team_ids = fields.Many2many('res.users', relation="broker_team_res_users_rel", string="Team Members", required=True)
