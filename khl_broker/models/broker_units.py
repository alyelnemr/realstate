# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, ValidationError



class BrokerUnits(models.Model):
    _name = 'broker.units'
    _inherit = ['mail.thread']
    name = fields.Char(string="Unit Name", required=True, tracking=True)
    unit_code = fields.Char(string="Unit Code", default='New')
    code = fields.Char(string="Code", required=True, tracking=True)
    project_id = fields.Many2one('unit.projects', string="Project Name")
    address = fields.Text(string="Address", tracking=True)
    price = fields.Float(string="Price", tracking=True)
    payment_plan = fields.Char(string="Payment Plan", tracking=True)
    notes = fields.Text(string="Notes", tracking=True)
    commission_percentage = fields.Float(string="Commission Percentage", required=True, tracking=True)
    commission = fields.Float(string="Commission", compute='compute_company_commission', store=True)
    space = fields.Float(string="Area")
    floor = fields.Integer(string="Floor")
    developer_company = fields.Many2one('res.partner', string="Developer Company", tracking=True)

    @api.depends('commission_percentage', 'price')
    def compute_company_commission(self):
        for rec in self:
            if rec.price and rec.commission_percentage:
                rec.commission = rec.price * (rec.commission_percentage / 100)
            else:
                rec.commission = 0.0

    state = fields.Selection([
        ('valid', 'Free'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
        ('invoiced', 'Invoiced'),
    ], 'State', index=True, default="valid", tracking=True)

    @api.onchange('developer_company')
    def onchange_developer_company(self):
        if self.developer_company:
            self.commission_percentage = self.developer_company.commission_percentage

    @api.model
    def create(self, vals):
        if not vals.get('unit_code') or vals['unit_code'] == _('New'):
            vals['unit_code'] = self.env['ir.sequence'].next_by_code('broker.units') or _('New')
        return super(BrokerUnits, self).create(vals)

    @api.constrains('floor')
    def constrains_floor(self):
        for rec in self:
            if rec.floor <= 0:
                raise ValidationError(_('You Should Add Floor'))
