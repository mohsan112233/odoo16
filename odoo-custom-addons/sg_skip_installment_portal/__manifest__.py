# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "SG Skip Installment Portal",
    'summary': """ SG Skip Installment Portal """,
    'description': """

    """,
    'category': '',
    'version': '1.0',
    'depends': ['hr', 'base', 'sync_employee_advance_salary', 'portal', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'security/data.xml',
        # 'views/assets.xml',
        # 'views/advance_approval_view.xml',
        'views/skip_request_form.xml',

    ],
    'demo': [

    ],
    'qweb': [

    ],

    'assets': {
        'web.assets_frontend': [
            'sg_skip_installment_portal/static/src/js/skip_installment.js',
        ],
    },
    # 'js': ['static/src/js/advance_portal.js'],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
