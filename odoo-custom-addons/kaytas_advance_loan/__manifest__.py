{
    'name': "KTAX Loan",
    'author': 'GlobalXS technology Solutions',
    'category': 'CRM',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': """
""",
    'version': '1.0',
    'depends': ['sync_employee_advance_salary'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/group.xml',
        'views/kaytas_payments.xml',
        # 'views/pay_fully_loan.xml',

         
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
