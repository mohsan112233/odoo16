# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "SG Attendance Adjust Portal",
    'summary': """ SG Attendance Adjust Portal """,
    'description': """

    """,
    'category': '',
    'version': '1.0',
    'depends': ['hr', 'hr_attendance', 'base','sg_attendance_adjustment_request','portal','website'],
    'data': [
        'security/ir.model.access.csv',
        'security/data.xml',
        # 'views/assets.xml',
        'views/website_form.xml',
        'views/attendance_view.xml',

    ],
    'demo': [

    ],
    'qweb': [

    ],

    'assets': {
        'web.assets_backend': [
            'sg_attendance_adjustment_portal/static/src/js/attendance_adjustment.js',
        ],
    },
    # 'js': ['static/src/js/attendance_adjustment.js'],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
