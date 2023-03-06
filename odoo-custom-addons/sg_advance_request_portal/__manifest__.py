# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "SG Advance Request Portal",
    'summary': """ SG Advance Request Portal """,
    'description': """

    """,
    'category': '',
    'version': '1.0',
    'depends': ['hr', 'base', 'sync_employee_advance_salary', 'portal', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'security/data.xml',
        # 'views/assets.xml',
        'views/advance_approval_view.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'assets': {
      'web.assets_frontend': [
          'sg_advance_request_portal/static/src/js/advance_portal.js',
      ],
    },
    # 'js': ['static/src/js/advance_portal.js'],

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
