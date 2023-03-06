# Part of odoo. See LICENSE file for full copyright and licensing details

{
    # Module Information
    'name': 'Employee Portal Time Off',
    'category': 'Website',
    'version': '1.0',
    'license': 'OPL-1',
    'summary': 'Portal user can manage leaves from Website Portal',
    'description': """
        Portal user can manage leaves from Website Portal
    """,
    # Dependencies
    'depends': [
        'website',
        'portal',
        'hr_holidays',
    ],
    # Views
    'data': [
        'security/ir.model.access.csv',
        # 'views/assets.xml',
        'views/templates.xml',
    ],
    # Author
    'author': 'Techinsider Solution',
    'website': 'http://www.techinsidersolution.com',
    # App Store Specific
    'images': ['static/description/emp_timeoff_poster_offer.png'],

    'assets': {
        'web.assets_frontend': [
            'employee_portal_timeoff/static/src/js/leave_portal.js',
            'employee_portal_timeoff/static/src/js/portal_timeoff.js',
            'employee_portal_timeoff/static/src/scss/custom_style.scss',
        ],
    },
    # Pricing
    'price': 149.00,
    'currency': 'EUR',
    # Technical
    'installable': True,
}
