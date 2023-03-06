{
    'name': "Stock Ledger Report",
    'author': 'Mohsan Raza',
    'category': 'Stock',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': "Stock Ledger",
    'version': '1.4',
    'depends': ['stock','report_xlsx', 'base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'reports/stock_ledger_report.xml',
        'reports/report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
