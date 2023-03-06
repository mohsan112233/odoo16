{
    'name': "Sale Order",
    'author': 'Mohsan Raza',
    'sequence': '-10000',
    'category': 'Invoicing',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': "Sale Invoices",
    'version': '16.11',
    'depends': ['contacts', 'sale', 'base', ],
    'data': [
        'views/views.xml',
        'reports/sale_order.xml',
        'reports/report.xml',
        'reports/sale_orders_tax_report.xml',
        'reports/sale_unregistered_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
