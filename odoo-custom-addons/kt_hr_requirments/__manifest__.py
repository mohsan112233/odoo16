# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Employee Agreement',
    'version': '1.0',
    'summary': 'Partners',

    'category': 'Accounting/Accounting',
    'website': 'https://www.odoo.com/page/billing',

    'depends': [
        'sync_employee_advance_salary',
        'hr_payroll',
        'hr_contract',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/emp.xml',
        'views/loan_view.xml',
        'views/blood_group.xml',
        'views/grade_view.xml',
        'views/view.xml',

    ],
    'demo': [

    ],

}
