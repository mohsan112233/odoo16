{
    'name': "Ghani Attendance",
    'author': 'GlobalXS technology Solutions',
    'category': 'CRM',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': """
""",
    'version': '1.0',
    'depends': ['hr_attendance', 'hr_payroll',  'sg_attendance_adjustment_request', 'hr_holidays'
        ,'employee_late_check_in'],
    'data': [
        'security/ir.model.access.csv',
        # 'security/group.xml'
        'views/attendance_adjustment_views.xml',

        # 'views/outdoor_work.xml',
        # 'views/remote_work.xml',
        # 'views/assumption_request.xml',
        # 'views/shift_change_request.xml',
        'views/settings.xml',
        'views/attendance_request.xml',

        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
