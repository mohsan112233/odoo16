{
    'name': "Sale Invoices",
    'author': 'Mohsan Raza',
    'category': 'Invoicing',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': "Sale Invoices",
    'version': '16.11',
    'depends': ['contacts', 'sale', 'base', 'account','report_xlsx'],
    'data': [
        'views/views.xml',
        'reports/sale_invoice.xml',
        'reports/report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
