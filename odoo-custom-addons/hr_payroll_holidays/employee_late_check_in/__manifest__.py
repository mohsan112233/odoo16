# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Ijaz Ahammed (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

{
    'name': 'Employee Late Check-in',
    'version': '13.0.1.0.0',
    'summary': """This module Allows Employee Late check-in deduction/penalty""",
    'description': """This module Allows Employee Late check-in deduction/penalty""",
    'author': "GlobalXS Technology Solutions",
    'company': 'GlobalXS Technology Solutions',
    'website': 'https://www.globalxs.co',
    'maintainer': 'GlobalXS Technology Solutions',
    'category': 'Human Resources',
    'depends': ['hr_attendance', 'hr_payroll', 'hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'security/late_security.xml',
        'data/cron.xml',
        'data/salary_rule.xml',
        'views/res_config_settings.xml',
        'views/hr_attendance_view.xml',
        'views/late_check_in_view.xml',
        'views/hr_employee.xml',
        'views/report_check_in.xml',

    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
