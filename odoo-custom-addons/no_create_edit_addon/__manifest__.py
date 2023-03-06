# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "No Edit Create",
    'author': 'Mohsan Raza',
    'category': 'Services',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': "Sale Purchase no edit create",
    'version': '1.0',
    'depends': ['sale'],
    'data': [
        'views/view_change_sale_purchase.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
