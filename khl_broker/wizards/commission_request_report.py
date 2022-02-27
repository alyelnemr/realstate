from datetime import date

from odoo import models, fields, api, _


class CommissionRequestReport(models.TransientModel):
    _name = 'commission.request.report'
    _description = 'Commission Request Report'
    broker_request_id = fields.Many2one('broker.request', string="Broker Request")
    report_type = fields.Selection(string="Report Type", selection=[('commission', 'Commission'),
                                                                    (
                                                                    'sales_person_incentive', 'Sales Person Incentive'),
                                                                    ('sales__manager_person_incentive',
                                                                     'Sales Manager Person Incentive')])

    def print(self):
        return self.env.ref('khl_broker.commission_request_report_id').report_action(self.id)
