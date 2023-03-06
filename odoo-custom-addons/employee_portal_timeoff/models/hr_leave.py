# Part of Odoo. See LICENSE file for full copyright and licensing details.

import random
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from datetime import datetime, time,date
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

from odoo.exceptions import AccessDenied
from odoo.exceptions import UserError

class EmpPortalTimeOff(models.Model):
    _inherit = "hr.leave"
    
    def update_timeoff_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        if not (values['description'] and values['timeoff_type'] and values['from'] and values['to']):
            return {
                'errors': _('All fields are required !')
            }
        emp = self.env['hr.employee'].sudo().search([('user_id.id', '=', user.id)], limit=1, order='id desc')
        date_from = values['from']
        date_from = datetime.strptime(date_from, "%Y-%m-%d")
        date_from = date_from.day
        date_to = values['to']
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
        date_to = date_to.day

        number_of_days = float(date_to) - float(date_from)
        self.from_date = date.today()

        self.to_date = date.today()

        # print(self.from_date.strftime('%Y-01-01'))
        print(self.from_date, 'llllllllllll', date.today(), self.to_date)
        from_1st_jun = date.today().strftime('%Y-01-01')
        today_month = date.today().month

        # if self.holiday_status_id.name == 'Annual Leave':
        annual_leave_type = self.env['hr.leave.allocation'].search([('name', '=', (values['timeoff_type']))])
        annual_leave = self.env['hr.leave.allocation'].search(
            ['&', ('holiday_status_id.name', '=', (values['timeoff_type']))
                , ('employee_id.id', '=', emp.id)], limit=1, order='id desc')
        print(annual_leave, annual_leave_type.name)

        total_annal = annual_leave.number_of_days_display
        pr_month = total_annal / 12
        today_month = int(today_month)
        if int(today_month) > 6:
            today_month = today_month - 6
            pr_month = pr_month * int(today_month)
            print(pr_month)
            count = 0
        else:
            today_month = today_month + 6
            pr_month = pr_month * int(today_month)
        count = 0
        annual_leaves = self.env['hr.leave'].search(
            [('employee_id.id', '=', emp.id), ('request_date_from', '>=', from_1st_jun),
             ('request_date_from', '<=', date.today()), ('state', '=', 'validate'),
             ('holiday_status_id.name', '=', (values['timeoff_type']))])
        for i in annual_leaves:
            count = count + i.number_of_days
        pr_month = pr_month - count
        print(pr_month, 'test0', count)
        number_of_days = number_of_days + 1
        if pr_month > 1:
            if number_of_days > pr_month:
                raise UserError((f'{emp.name} can get  maximum {round(pr_month, 2)}'))
        else:
            number_of_days = pr_month
        annual_leaves123 = self.env['hr.leave.type'].search(
            [('name', '=', (values['timeoff_type']))], limit=1, order='id desc')
        value = {
            'number_of_days': number_of_days,
            'employee_id': emp.id,
            'name': values['description'],
            'holiday_status_id': annual_leaves123.id,
            'request_date_from': values['from'],
            'request_date_to': values['to'],
            'date_from': values['from'],
            'date_to': values['to'],
            'request_unit_half': values['half_day'],
            'request_unit_hours': values['custom_hours'],
            'request_hour_from': values['request_hour_from'],
            'request_hour_to': values['request_hour_to'],
            'request_date_from_period': values['request_date_from_period'],
            }
        if values['timeoffID']:
            timeoff_rec = self.env['hr.leave'].sudo().browse(values['timeoffID'])
            if timeoff_rec:
                timeoff_rec.sudo().write(value)
                # timeoff_rec._onchange_request_parameters()

    @api.model
    def create_timeoff_portal(self, values):
        if not (self.env.user.employee_id):
            raise AccessDenied()
        user = self.env.user
        self = self.sudo()
        if not (values['description'] and values['timeoff_type'] and values['from'] and values['to']):
            return {
                'errors': _('All fields are required !')
            }
        emp = self.env['hr.employee'].sudo().search([('user_id.id', '=', user.id)],limit=1, order='id desc')
        date_from = values['from']
        date_from = datetime.strptime(date_from, "%Y-%m-%d")
        date_from = date_from.day
        date_to = values['to']
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
        date_to = date_to.day

        number_of_days = float(date_to) - float(date_from)
        self.from_date = date.today()

        self.to_date = date.today()

        # print(self.from_date.strftime('%Y-01-01'))
        print(self.from_date,'llllllllllll',date.today(),self.to_date)
        from_1st_jun = date.today().strftime('%Y-01-01')
        today_month = date.today().month


        # if self.holiday_status_id.name == 'Annual Leave':
        annual_leave_type = self.env['hr.leave.allocation'].search([('name','=',(values['timeoff_type']))])
        annual_leave = self.env['hr.leave.allocation'].search(
            ['&', ('holiday_status_id.name', '=', (values['timeoff_type']))
                , ('employee_id.id', '=', emp.id)],limit=1, order='id desc')
        print(annual_leave,annual_leave_type.name)

        total_annal = annual_leave.number_of_days_display
        pr_month = total_annal / 12
        today_month = int(today_month)
        if int(today_month) > 6:
            today_month = today_month - 6
            pr_month = pr_month * int(today_month)
            print(pr_month)
            count = 0
        else:
            today_month = today_month + 6
            pr_month = pr_month * int(today_month)
        count = 0
        annual_leaves = self.env['hr.leave'].search(
            [('employee_id.id', '=', emp.id), ('request_date_from', '>=', from_1st_jun),
             ('request_date_from', '<=', date.today()), ('state', '=', 'validate'),
             ('holiday_status_id.name', '=', (values['timeoff_type']))])
        for i in annual_leaves:
            count = count + i.number_of_days
        pr_month = pr_month - count

        number_of_days = number_of_days + 1
        if pr_month > 1:
            if number_of_days > pr_month:
                raise UserError((f'{emp.name} can get  maximum {round(pr_month,2)}'))
        else:
            number_of_days = pr_month
        print(values['from'],)
        annual_leaves123 = self.env['hr.leave.type'].search(
            [ ('name', '=', (values['timeoff_type']))],limit=1, order='id desc')
        values = {
            'number_of_days':number_of_days,
            'employee_id':emp.id,
            'name': values['description'],
            'holiday_status_id': annual_leaves123.id,
            'request_date_from': values['from'],
            'request_date_to': values['to'],
            'date_from': values['from'],
            'date_to': values['to'],
            'request_unit_half': values['half_day'],
            'request_unit_hours': values['custom_hours'],
            'request_hour_from': values['request_hour_from'],
            'request_hour_to': values['request_hour_to'],
            'request_date_from_period': values['request_date_from_period'],
        }
        print('this',values)
        tmp_leave = self.env['hr.leave'].sudo().search([('employee_id.user_id.id', '=', user.id)])
        # tmp_leave._onchange_request_parameters()
        # values  = tmp_leave._convert_to_write(tmp_leave._cache)
        mytimeoff = self.env['hr.leave'].sudo().create(values)
        return {
            'id': mytimeoff.id
        }
