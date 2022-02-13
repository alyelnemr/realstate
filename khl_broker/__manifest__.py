{
    'name': "KHL Broker Management",

    'summary': """
        KHL Broker Management
        """,

    'description': """
        KHL Broker Management
    """,
    'version': '1.0.0',
    'depends': [
        'base',
        'mail',
        'account',
        'contacts',
        'hr_payroll',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security_groups.xml',
        'data/broker_units_seq.xml',
        'views/broker_units.xml',
        'views/broker_request.xml',
        'views/sales_target.xml',
        'views/unit_projects.xml',
        'views/units_pre_contract.xml',
        'views/mobile_data.xml',
        'views/broker_teams.xml',
        'views/broker_bouns.xml',
        'views/unit_reservation_report.xml',
        'views/contract_report.xml',
        'views/emp_sales_target_report.xml',
        'views/sales_person_commissions_report.xml',
        'views/bouns_commissions_report.xml',
        'views/incentive_commissions_report.xml',
        'views/hr_employee_inherit.xml',
        'views/res_partner_view.xml',
        'views/emp_sales_target.xml',
        'wizards/emp_sales_target_report.xml',
        'views/menus.xml'
    ],
    'demo': [
    ],
}
# -*- coding: utf-8 -*-
