# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResUsers(models.Model):
    _name = 'broker.request.users'
    _rec_name = 'broker_request_id'

    broker_request_id = fields.Many2one('broker.request', string="Broker Request")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    coach_id = fields.Many2one('hr.employee', related='employee_id.coach_id', readonly=1, store=1)
    parent_id = fields.Many2one('hr.employee', related='employee_id.parent_id', readonly=1, store=1)
    job_id = fields.Many2one('hr.job', string="Job Position", related='employee_id.job_id', readonly=1)
