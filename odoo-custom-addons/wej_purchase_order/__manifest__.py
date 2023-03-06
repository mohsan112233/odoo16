{
    'name': "Purchase Order Reports",
    'author': 'Mohsan Raza',
    'category': 'Invoicing',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': "Purchase Order",
    'version': '16.11',
    'depends': ['purchase'],
    'data': [
        'views/views.xml',
        'reports/purchase_order_report.xml',
        'reports/report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
