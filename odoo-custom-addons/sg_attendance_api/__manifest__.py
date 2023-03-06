# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "SG Attendance Api",
    'summary': """ SG Attendance Api """,
    'description': """

    """,
    'category': '',
    'version': '1.0',
    'depends': ['hr_attendance','portal','website'],
    'data': [
        'views/attendance_location.xml',

    ],
    'demo': [

    ],
    'qweb': [

    ],
    # 'js': ['static/src/js/attendance_adjustment.js'],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
