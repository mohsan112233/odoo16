{
    'name': "Delivery Reports",
    'author': 'Mohsan Raza',
    'category': 'Invoicing',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': "Delivery Reports",
    'version': '16.11',
    'depends': ['contacts', 'sale', 'base'],
    'data': [
        'views/views.xml',
        'reports/delivery.xml',
        'reports/report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
