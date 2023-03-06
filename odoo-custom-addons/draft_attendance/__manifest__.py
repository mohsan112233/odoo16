{
    'name': 'Draft Attendance',
    'version': '15.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Module for manging the draft attendance',
    'sequence': '-100',
    'license': 'AGPL-3',
    'author': 'Hasnain JUtt',
    'Maintainer': 'Odoo Mates',
    'website': 'odoomates.com',
    'depends': [
        'hr_attendance',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/draft_attendance.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
