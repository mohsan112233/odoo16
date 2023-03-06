{
    'name': "Product Sequence",
    'author': 'GlobalXS technology Solutions',
    'category': 'CRM',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': """
""",
    'version': '1.0',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/group.xml',
        'views/views.xml',
        'views/master_record_views.xml',

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
