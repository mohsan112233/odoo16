{
    'name': "Sale Assortment",
    'author': 'GlobalXS technology Solutions',
    'category': 'CRM',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': """
""",
    'version': '1.0',
    'depends': ['sale','stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/assortment.xml',
        'views/assortment_page.xml',
        'wizard/sale.xml',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
