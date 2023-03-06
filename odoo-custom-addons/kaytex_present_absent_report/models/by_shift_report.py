import time
import math
# import datetime
import logging
from datetime import date

import calendar

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

from io import StringIO
import io

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

import pytz
from odoo import models, fields, api
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from datetime import date as delta1
    # timedelta as td


class AttendanceReport(models.TransientModel):
    _name = 'attendance.report.shift'
    _description = "Attendance Report Wizard"

    from_date = fields.Date('From Date specific', default=lambda self: fields.Date.to_string(delta1.today()),
                            required=True)
    to_date = fields.Date("To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    shift_id = fields.Many2one('resource.calendar',string='Shift')
    date = fields.Date(string='Date',default=date.today())
    print_by = fields.Selection([
        ('4', "On Leave"),
        ('2', "Present"),
        ('3', "Absent"),
        ('1', "All"),

    ], string="View Status", default='1')
    def print_report_spesific(self ,mode='date'):
        print(delta1.today())

        global month_date, shift, total_early_out_days, total_late_days, punctuality, total_pay_days, regularity
        shift_name = 'No Shift Assigned'  # for shift
        date = []  # for date range
        day = []  # for date range
        datas = []
        employee = []
        reporting = []
        new_format = "%H:%M:%S"

        # for rec in date:
        # day_check = rec.strftime("%A")


        check_in = ' '
        check_out = ' '
        late_arrival = 0.0
        early_depart = 0.0
        work_hr = 0.0
        punctuality = 0
        present = 0
        regularity = 0
        total_early_out_days = 0
        total_late_days = 0
        total_pay_days = 0.0

        planning_record_test = self.env["hr.employee"].search([
            ('resource_calendar_id', '=', self.shift_id.id)])
        print(planning_record_test)
        for i in planning_record_test:
            # planning_record = self.env["planning.slot"].search(
            #     [('employee_id', '=', i.name), ('new_date', '>=', self.from_date)])
            # print('planning_record',planning_record)
            # shift_name = 'No Shift Assigned'
            # for plan in planning_record:
            #     if not plan.start_datetime:
            #         shift_name = ('---')
            #     elif plan:
            #         shift_start = plan.start_datetime
            #         shift_start = shift_start.astimezone(pytz.timezone('Asia/Karachi'))
            #         shift_start = shift_start.strftime(new_format)
            #         shift_end = plan.end_datetime
            #         shift_end = shift_end.astimezone(pytz.timezone('Asia/Karachi'))
            #         shift_end = shift_end.strftime(new_format)
            #         print(shift_start)
            #         print(shift_end)
            #         shift_name = str(shift_start) + '-' + str(shift_end)
            #
            # # leave = self.env["hr.leave.report"].search(
            # #     [('employee_id', '=', i.name)
            # #       , ('date_from', '=', datetime.today())])

            leave = self.env["hr.leave"].search_count(
                [('employee_id', '=', i.name), ('state', '=', 'validate'), ('request_date_from', '<=', self.date),
                 ('request_date_to', '>=', self.date)])

            # leave_global = self.env["hr.leave"].search_count(
            #     [('employee_id', '=', i.name),('request_date_from', '<=', datetime.today()),
            #      ('request_date_to', '>=', datetime.today()),('holiday_status_id', '=', 'Global holiday')
            #      , ('state', '=', 'validate')])
            # print(leave,'lllllllllll',leave_global)
            # print('rec', leave.holiday_status_id)
            attendance = self.env["hr.attendance"].search([('employee_id', '=', i.name),
                ('checkin_date', '=', self.date)])
            print('attend', attendance)
            if attendance.check_in:
                check_in = attendance.check_in
                check_in = check_in.astimezone(pytz.timezone('Asia/Karachi'))
                check_in = check_in.strftime(new_format)
                status = 'Present'

            if attendance.check_out:
                check_out = attendance.check_out
                check_out = check_out.astimezone(pytz.timezone('Asia/Karachi'))
                check_out = check_out.strftime(new_format)
            else:
                check_out = "Not Marked"
            late_arrival = attendance.late_emp
            early_depart = attendance.overtime

            day_check = delta1.today().strftime("%A")
            if not attendance:
                status = 'Absent'
                check_in = "Not Mark"
            # leave = self.env["hr.leave"].search_count(
            #     [('employee_id', '=', i.name)
            #         , ('request_date_from', '=', delta1.today())])
            # print('rec', leave)
            date_day = self.date
            day_check = date_day.strftime("%A")
            if day_check == 'Monday':
                check = 0
            if day_check == 'Tuesday':
                check = 1
            if day_check == 'Wednesday':
                check = 2
            if day_check == 'Thursday':
                check = 3
            if day_check == 'Friday':
                check = 4
            if day_check == 'Saturday':
                check = 5
            if day_check == 'Sunday':
                check = 6
            plan = self.env['hr.contract.history'].search(
                [('employee_id', '=', i.id)])
            plan = plan.resource_calendar_id
            plan_day_name = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', self.shift_id.id), ('dayofweek', '=', check)])
            if not plan_day_name:
                shift = 'No Shift Assign'
                status = 'No Shift Assign'
                check_in = "No Shift Assign"
                check_out = "No Shift Assign"
            print(i.name,plan_day_name,day_check)
            for rec in plan_day_name:
                # stuff.plan_date_only = rec.new_date
                planned_time = rec.hour_from
                planned_exit_time = rec.hour_to
                shift = str(rec.hour_from) + ' ' +'-'+' '  + str(rec.hour_to)
            if leave:
                status = 'Leave Day'
                check_in = "Leave Day"
                check_out = "Leave Day"
            if day_check == 'Sunday':
                status = 'Rest Day'
                check_in = "Rest Day"
                check_out = "Rest Day"
            # if leave_global:
            #     status = "Global Leave Day"
            #     check_in = "Global Leave Day"
            #     check_out = "Global Leave Day"
            #     shift_name = "Global Leave Day"
            # if shift_name == "No Shift Assigned":
            #     check_in = "Rest Day"
            #     check_out = "Rest Day"
            #     status = "Rest Day"
            datas.append({
                'code': i.barcode,
                'name': i.name,
                'job_id': i.job_id.name,
                'department_id': i.department_id.name,
                'shift': shift,
                'check_in': check_in,
                'check_out': check_out,

                'late_arrival': late_arrival,
                'early_depart': early_depart,
                'status': status,
            })
        select_companies = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        select_companies = select_companies[0]
        res = {
            'employee_rec': employee,
            'attendances': datas,
            'reporting': reporting,
            'start_date': self.from_date,
            'end_date': self.to_date,
            'com':select_companies.name

        }
        data = {
            'form': res,
        }
        return self.env.ref('kaytex_present_absent_report.report_hr_attendance_test').report_action([], data=data)


    def print_report_spesific_present(self ,mode='date'):
        print(delta1.today())

        global month_date, shift, total_early_out_days, total_late_days, punctuality, total_pay_days, regularity
        shift_name = 'No Shift Assigned'  # for shift
        date = []  # for date range
        day = []  # for date range
        datas = []
        employee = []
        reporting = []
        new_format = "%H:%M:%S"

        # for rec in date:
        # day_check = rec.strftime("%A")


        check_in = ' '
        check_out = ' '
        late_arrival = 0.0
        early_depart = 0.0
        work_hr = 0.0
        punctuality = 0
        present = 0
        regularity = 0
        total_early_out_days = 0
        total_late_days = 0
        total_pay_days = 0.0

        planning_record_test = self.env["hr.employee"].search([
            ('resource_calendar_id', '=', self.shift_id.id)])

        for i in planning_record_test:
            # planning_record = self.env["planning.slot"].search(
            #     [('employee_id', '=', i.name), ('new_date', '>=', self.from_date)])
            # print('planning_record',planning_record)
            # shift_name = 'No Shift Assigned'
            # for plan in planning_record:
            #     if not plan.start_datetime:
            #         shift_name = ('---')
            #     elif plan:
            #         shift_start = plan.start_datetime
            #         shift_start = shift_start.astimezone(pytz.timezone('Asia/Karachi'))
            #         shift_start = shift_start.strftime(new_format)
            #         shift_end = plan.end_datetime
            #         shift_end = shift_end.astimezone(pytz.timezone('Asia/Karachi'))
            #         shift_end = shift_end.strftime(new_format)
            #         print(shift_start)
            #         print(shift_end)
            #         shift_name = str(shift_start) + '-' + str(shift_end)
            #
            # # leave = self.env["hr.leave.report"].search(
            # #     [('employee_id', '=', i.name)
            # #       , ('date_from', '=', datetime.today())])

            leave = self.env["hr.leave"].search_count(
                [('employee_id', '=', i.name), ('state', '=', 'validate'), ('request_date_from', '<=', self.date),
                 ('request_date_to', '>=', self.date)])

            # leave_global = self.env["hr.leave"].search_count(
            #     [('employee_id', '=', i.name),('request_date_from', '<=', datetime.today()),
            #      ('request_date_to', '>=', datetime.today()),('holiday_status_id', '=', 'Global holiday')
            #      , ('state', '=', 'validate')])
            # print(leave,'lllllllllll',leave_global)
            # print('rec', leave.holiday_status_id)
            attendance = self.env["hr.attendance"].search([('employee_id', '=', i.name),
                ('checkin_date', '=', self.date)])
            print('attend', attendance)
            if attendance.check_in:
                check_in = attendance.check_in
                check_in = check_in.astimezone(pytz.timezone('Asia/Karachi'))
                check_in = check_in.strftime(new_format)
                status = 'Present'
            #     if attendance.check_out and attendance.check_in and attendance.planned_exit and attendance.planned_date:
            #         per = attendance.check_out - attendance.check_in
            #
            #         pland = attendance.planned_exit - attendance.planned_date
            #         present_per = (per / pland) * 100
            #         if present_per > 95:
            #
            #             status = 'Present'
            #         elif present_per < 50:
            #
            #             leave_half_day = self.env["hr.leave"].search(
            #                 [('employee_id', '=', i.name), ('request_date_from', '<=', datetime.today()),
            #                  ('request_date_to', '>=', datetime.today()),
            #                  ('holiday_status_id', '!=', 'Unpaid')
            #                     , ('state', '=', 'validate')])
            #             print(leave_half_day, '}}}}}}}}}}]]]]')
            #             if leave_half_day:
            #
            #                 status = 'Half Day'
            #             else:
            #
            #                 status = 'Absent'
            #
            #
            #         elif present_per > 50 and present_per < 76:
            #             leave_half_day = self.env["hr.leave"].search(
            #                 [('employee_id', '=', i.name), ('request_date_from', '<=', datetime.today()),
            #                  ('request_date_to', '>=', datetime.today()),
            #                  ('holiday_status_id', '!=', 'Unpaid')
            #                     , ('state', '=', 'validate')])
            #             if leave_half_day:
            #                 status = 'Present/HL'
            #             else:
            #                 status = 'Present/HA'
            #         elif present_per >= 76 and present_per < 95:
            #             leave_half_day = self.env["hr.leave"].search(
            #                 [('employee_id', '=', i.name), ('request_date_from', '<=', datetime.today()),
            #                  ('request_date_to', '>=', datetime.today()),
            #                  ('holiday_status_id', '!=', 'Unpaid')
            #                     , ('state', '=', 'validate')])
            #             if leave_half_day:
            #                 status = 'Present/SL'
            #             else:
            #                 status = 'Present/SA'
            #         elif present_per >= 76 and present_per < 95:
            #
            #             status = 'Present/SL'
            #
            #
            #     elif not attend.check_out:
            #
            #         status = 'On duty'
            #     elif not attend.planned_exit or not attend.planned_date:
            #         status = 'No Planning'
            #
            # else:
            #     check_in = "Not Marked"
            #     status = 'Absent'
            if attendance.check_out:
                check_out = attendance.check_out
                check_out = check_out.astimezone(pytz.timezone('Asia/Karachi'))
                check_out = check_out.strftime(new_format)
            else:
                check_out = "Not Marked"
            late_arrival = attendance.late_emp
            early_depart = attendance.overtime

            day_check = delta1.today().strftime("%A")
            if not attendance:
                status = 'Absent'
                check_in = "Not Mark"
            # leave = self.env["hr.leave"].search_count(
            #     [('employee_id', '=', i.name)
            #         , ('request_date_from', '=', delta1.today())])
            # print('rec', leave)
            date_day = self.date
            day_check = date_day.strftime("%A")
            if day_check == 'Monday':
                check = 0
            if day_check == 'Tuesday':
                check = 1
            if day_check == 'Wednesday':
                check = 2
            if day_check == 'Thursday':
                check = 3
            if day_check == 'Friday':
                check = 4
            if day_check == 'Saturday':
                check = 5
            if day_check == 'Sunday':
                check = 6
            plan = self.env['hr.contract.history'].search(
                [('employee_id', '=', i.id)])
            plan = plan.resource_calendar_id
            plan_day_name = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', self.shift_id.id), ('dayofweek', '=', check)])
            if not plan_day_name:
                shift = 'No Shift Assign'
                status = 'No Shift Assign'
                check_in = "No Shift Assign"
                check_out = "No Shift Assign"
            for rec in plan_day_name:
                # stuff.plan_date_only = rec.new_date
                planned_time = rec.hour_from
                planned_exit_time = rec.hour_to
                shift = str(rec.hour_from) + ' ' +'-'+' '  + str(rec.hour_to)
            if leave:
                status = 'Leave Day'
                check_in = "Leave Day"
                check_out = "Leave Day"
            if day_check == 'Sunday':
                status = 'Rest Day'
                check_in = "Rest Day"
                check_out = "Rest Day"
            # if leave_global:
            #     status = "Global Leave Day"
            #     check_in = "Global Leave Day"
            #     check_out = "Global Leave Day"
            #     shift_name = "Global Leave Day"
            # if shift_name == "No Shift Assigned":
            #     check_in = "Rest Day"
            #     check_out = "Rest Day"
            #     status = "Rest Day"
            if attendance and not leave:
                datas.append({
                    'code': i.barcode,
                    'name': i.name,
                    'job_id': i.job_id.name,
                    'department_id': i.department_id.name,
                    'shift': shift,
                    'check_in': check_in,
                    'check_out': check_out,

                    'late_arrival': late_arrival,
                    'early_depart': early_depart,
                    'status': status,
                })
        select_companies = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        select_companies = select_companies[0]
        res = {
            'employee_rec': employee,
            'attendances': datas,
            'reporting': reporting,
            'start_date': self.from_date,
            'end_date': self.to_date,
            'com':select_companies.name

        }
        data = {
            'form': res,
        }
        return self.env.ref('kaytex_present_absent_report.report_hr_attendance_test').report_action([], data=data)


    def print_report_spesific_absent(self ,mode='date'):
        print(delta1.today())

        global month_date, shift, total_early_out_days, total_late_days, punctuality, total_pay_days, regularity
        shift_name = 'No Shift Assigned'  # for shift
        date = []  # for date range
        day = []  # for date range
        datas = []
        employee = []
        reporting = []
        new_format = "%H:%M:%S"

        # for rec in date:
        # day_check = rec.strftime("%A")


        check_in = ' '
        check_out = ' '
        late_arrival = 0.0
        early_depart = 0.0
        work_hr = 0.0
        punctuality = 0
        present = 0
        regularity = 0
        total_early_out_days = 0
        total_late_days = 0
        total_pay_days = 0.0

        planning_record_test = self.env["hr.employee"].search([
            ('resource_calendar_id', '=', self.shift_id.id)])

        for i in planning_record_test:
            # planning_record = self.env["planning.slot"].search(
            #     [('employee_id', '=', i.name), ('new_date', '>=', self.from_date)])
            # print('planning_record',planning_record)
            # shift_name = 'No Shift Assigned'
            # for plan in planning_record:
            #     if not plan.start_datetime:
            #         shift_name = ('---')
            #     elif plan:
            #         shift_start = plan.start_datetime
            #         shift_start = shift_start.astimezone(pytz.timezone('Asia/Karachi'))
            #         shift_start = shift_start.strftime(new_format)
            #         shift_end = plan.end_datetime
            #         shift_end = shift_end.astimezone(pytz.timezone('Asia/Karachi'))
            #         shift_end = shift_end.strftime(new_format)
            #         print(shift_start)
            #         print(shift_end)
            #         shift_name = str(shift_start) + '-' + str(shift_end)
            #
            # # leave = self.env["hr.leave.report"].search(
            # #     [('employee_id', '=', i.name)
            # #       , ('date_from', '=', datetime.today())])

            leave = self.env["hr.leave"].search_count(
                [('employee_id', '=', i.name), ('state', '=', 'validate'), ('request_date_from', '<=', self.date),
                 ('request_date_to', '>=', self.date)])

            # leave_global = self.env["hr.leave"].search_count(
            #     [('employee_id', '=', i.name),('request_date_from', '<=', datetime.today()),
            #      ('request_date_to', '>=', datetime.today()),('holiday_status_id', '=', 'Global holiday')
            #      , ('state', '=', 'validate')])
            # print(leave,'lllllllllll',leave_global)
            # print('rec', leave.holiday_status_id)
            attendance = self.env["hr.attendance"].search([('employee_id', '=', i.name),
                ('checkin_date', '=', self.date)])
            print('attend', attendance)
            if attendance.check_in:
                check_in = attendance.check_in
                check_in = check_in.astimezone(pytz.timezone('Asia/Karachi'))
                check_in = check_in.strftime(new_format)
                status = 'Present'
            #     if attendance.check_out and attendance.check_in and attendance.planned_exit and attendance.planned_date:
            #         per = attendance.check_out - attendance.check_in
            #
            #         pland = attendance.planned_exit - attendance.planned_date
            #         present_per = (per / pland) * 100
            #         if present_per > 95:
            #
            #             status = 'Present'
            #         elif present_per < 50:
            #
            #             leave_half_day = self.env["hr.leave"].search(
            #                 [('employee_id', '=', i.name), ('request_date_from', '<=', datetime.today()),
            #                  ('request_date_to', '>=', datetime.today()),
            #                  ('holiday_status_id', '!=', 'Unpaid')
            #                     , ('state', '=', 'validate')])
            #             print(leave_half_day, '}}}}}}}}}}]]]]')
            #             if leave_half_day:
            #
            #                 status = 'Half Day'
            #             else:
            #
            #                 status = 'Absent'
            #
            #
            #         elif present_per > 50 and present_per < 76:
            #             leave_half_day = self.env["hr.leave"].search(
            #                 [('employee_id', '=', i.name), ('request_date_from', '<=', datetime.today()),
            #                  ('request_date_to', '>=', datetime.today()),
            #                  ('holiday_status_id', '!=', 'Unpaid')
            #                     , ('state', '=', 'validate')])
            #             if leave_half_day:
            #                 status = 'Present/HL'
            #             else:
            #                 status = 'Present/HA'
            #         elif present_per >= 76 and present_per < 95:
            #             leave_half_day = self.env["hr.leave"].search(
            #                 [('employee_id', '=', i.name), ('request_date_from', '<=', datetime.today()),
            #                  ('request_date_to', '>=', datetime.today()),
            #                  ('holiday_status_id', '!=', 'Unpaid')
            #                     , ('state', '=', 'validate')])
            #             if leave_half_day:
            #                 status = 'Present/SL'
            #             else:
            #                 status = 'Present/SA'
            #         elif present_per >= 76 and present_per < 95:
            #
            #             status = 'Present/SL'
            #
            #
            #     elif not attend.check_out:
            #
            #         status = 'On duty'
            #     elif not attend.planned_exit or not attend.planned_date:
            #         status = 'No Planning'
            #
            # else:
            #     check_in = "Not Marked"
            #     status = 'Absent'
            if attendance.check_out:
                check_out = attendance.check_out
                check_out = check_out.astimezone(pytz.timezone('Asia/Karachi'))
                check_out = check_out.strftime(new_format)
            else:
                check_out = "Not Marked"
            late_arrival = attendance.late_emp
            early_depart = attendance.overtime

            day_check = delta1.today().strftime("%A")
            if not attendance:
                status = 'Absent'
                check_in = "Not Mark"
            # leave = self.env["hr.leave"].search_count(
            #     [('employee_id', '=', i.name)
            #         , ('request_date_from', '=', delta1.today())])
            # print('rec', leave)
            date_day = self.date
            day_check = date_day.strftime("%A")
            if day_check == 'Monday':
                check = 0
            if day_check == 'Tuesday':
                check = 1
            if day_check == 'Wednesday':
                check = 2
            if day_check == 'Thursday':
                check = 3
            if day_check == 'Friday':
                check = 4
            if day_check == 'Saturday':
                check = 5
            if day_check == 'Sunday':
                check = 6
            plan = self.env['hr.contract.history'].search(
                [('employee_id', '=', i.id)])
            plan = plan.resource_calendar_id
            plan_day_name = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', self.shift_id.id), ('dayofweek', '=', check)])
            if not plan_day_name:
                shift = 'No Shift Assign'
                status = 'No Shift Assign'
                check_in = "No Shift Assign"
                check_out = "No Shift Assign"
            for rec in plan_day_name:
                # stuff.plan_date_only = rec.new_date
                planned_time = rec.hour_from
                planned_exit_time = rec.hour_to
                shift = str(rec.hour_from) + ' ' +'-'+' '  + str(rec.hour_to)
            if leave:
                status = 'Leave Day'
                check_in = "Leave Day"
                check_out = "Leave Day"
            if day_check == 'Sunday':
                status = 'Rest Day'
                check_in = "Rest Day"
                check_out = "Rest Day"
            # if leave_global:
            #     status = "Global Leave Day"
            #     check_in = "Global Leave Day"
            #     check_out = "Global Leave Day"
            #     shift_name = "Global Leave Day"
            # if shift_name == "No Shift Assigned":
            #     check_in = "Rest Day"
            #     check_out = "Rest Day"
            #     status = "Rest Day"
            if not attendance and not leave:
                datas.append({
                    'code': i.barcode,
                    'name': i.name,
                    'job_id': i.job_id.name,
                    'department_id': i.department_id.name,
                    'shift': shift,
                    'check_in': check_in,
                    'check_out': check_out,

                    'late_arrival': late_arrival,
                    'early_depart': early_depart,
                    'status': status,
                })
        select_companies = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        select_companies = select_companies[0]
        res = {
            'employee_rec': employee,
            'attendances': datas,
            'reporting': reporting,
            'start_date': self.from_date,
            'end_date': self.to_date,
            'com':select_companies.name

        }
        data = {
            'form': res,
        }
        return self.env.ref('kaytex_present_absent_report.report_hr_attendance_test').report_action([], data=data)


    def print_report_spesific_leave(self ,mode='date'):
        print(delta1.today())

        global month_date, shift, total_early_out_days, total_late_days, punctuality, total_pay_days, regularity
        shift_name = 'No Shift Assigned'  # for shift
        date = []  # for date range
        day = []  # for date range
        datas = []
        employee = []
        reporting = []
        new_format = "%H:%M:%S"

        # for rec in date:
        # day_check = rec.strftime("%A")


        check_in = ' '
        check_out = ' '
        late_arrival = 0.0
        early_depart = 0.0
        work_hr = 0.0
        punctuality = 0
        present = 0
        regularity = 0
        total_early_out_days = 0
        total_late_days = 0
        total_pay_days = 0.0

        planning_record_test = self.env["hr.employee"].search([
            ('resource_calendar_id', '=', self.shift_id.id)])

        for i in planning_record_test:
            # planning_record = self.env["planning.slot"].search(
            #     [('employee_id', '=', i.name), ('new_date', '>=', self.from_date)])
            # print('planning_record',planning_record)
            # shift_name = 'No Shift Assigned'
            # for plan in planning_record:
            #     if not plan.start_datetime:
            #         shift_name = ('---')
            #     elif plan:
            #         shift_start = plan.start_datetime
            #         shift_start = shift_start.astimezone(pytz.timezone('Asia/Karachi'))
            #         shift_start = shift_start.strftime(new_format)
            #         shift_end = plan.end_datetime
            #         shift_end = shift_end.astimezone(pytz.timezone('Asia/Karachi'))
            #         shift_end = shift_end.strftime(new_format)
            #         print(shift_start)
            #         print(shift_end)
            #         shift_name = str(shift_start) + '-' + str(shift_end)
            #
            # # leave = self.env["hr.leave.report"].search(
            # #     [('employee_id', '=', i.name)
            # #       , ('date_from', '=', datetime.today())])

            leave = self.env["hr.leave"].search_count(
                [('employee_id', '=', i.name), ('state', '=', 'validate'), ('request_date_from', '<=', self.date),
                 ('request_date_to', '>=', self.date)])

            # leave_global = self.env["hr.leave"].search_count(
            #     [('employee_id', '=', i.name),('request_date_from', '<=', datetime.today()),
            #      ('request_date_to', '>=', datetime.today()),('holiday_status_id', '=', 'Global holiday')
            #      , ('state', '=', 'validate')])
            # print(leave,'lllllllllll',leave_global)
            # print('rec', leave.holiday_status_id)
            attendance = self.env["hr.attendance"].search([('employee_id', '=', i.name),
                ('checkin_date', '=', self.date)])
            print('attend', attendance)
            if attendance.check_in:
                check_in = attendance.check_in
                check_in = check_in.astimezone(pytz.timezone('Asia/Karachi'))
                check_in = check_in.strftime(new_format)
                status = 'Present'
            #     if attendance.check_out and attendance.check_in and attendance.planned_exit and attendance.planned_date:
            #         per = attendance.check_out - attendance.check_in
            #
            #         pland = attendance.planned_exit - attendance.planned_date
            #         present_per = (per / pland) * 100
            #         if present_per > 95:
            #
            #             status = 'Present'
            #         elif present_per < 50:
            #
            #             leave_half_day = self.env["hr.leave"].search(
            #                 [('employee_id', '=', i.name), ('request_date_from', '<=', datetime.today()),
            #                  ('request_date_to', '>=', datetime.today()),
            #                  ('holiday_status_id', '!=', 'Unpaid')
            #                     , ('state', '=', 'validate')])
            #             print(leave_half_day, '}}}}}}}}}}]]]]')
            #             if leave_half_day:
            #
            #                 status = 'Half Day'
            #             else:
            #
            #                 status = 'Absent'
            #
            #
            #         elif present_per > 50 and present_per < 76:
            #             leave_half_day = self.env["hr.leave"].search(
            #                 [('employee_id', '=', i.name), ('request_date_from', '<=', datetime.today()),
            #                  ('request_date_to', '>=', datetime.today()),
            #                  ('holiday_status_id', '!=', 'Unpaid')
            #                     , ('state', '=', 'validate')])
            #             if leave_half_day:
            #                 status = 'Present/HL'
            #             else:
            #                 status = 'Present/HA'
            #         elif present_per >= 76 and present_per < 95:
            #             leave_half_day = self.env["hr.leave"].search(
            #                 [('employee_id', '=', i.name), ('request_date_from', '<=', datetime.today()),
            #                  ('request_date_to', '>=', datetime.today()),
            #                  ('holiday_status_id', '!=', 'Unpaid')
            #                     , ('state', '=', 'validate')])
            #             if leave_half_day:
            #                 status = 'Present/SL'
            #             else:
            #                 status = 'Present/SA'
            #         elif present_per >= 76 and present_per < 95:
            #
            #             status = 'Present/SL'
            #
            #
            #     elif not attend.check_out:
            #
            #         status = 'On duty'
            #     elif not attend.planned_exit or not attend.planned_date:
            #         status = 'No Planning'
            #
            # else:
            #     check_in = "Not Marked"
            #     status = 'Absent'
            if attendance.check_out:
                check_out = attendance.check_out
                check_out = check_out.astimezone(pytz.timezone('Asia/Karachi'))
                check_out = check_out.strftime(new_format)
            else:
                check_out = "Not Marked"
            late_arrival = attendance.late_emp
            early_depart = attendance.overtime

            day_check = delta1.today().strftime("%A")
            if not attendance:
                status = 'Absent'
                check_in = "Not Mark"
            # leave = self.env["hr.leave"].search_count(
            #     [('employee_id', '=', i.name)
            #         , ('request_date_from', '=', delta1.today())])
            # print('rec', leave)
            date_day = self.date
            day_check = date_day.strftime("%A")
            if day_check == 'Monday':
                check = 0
            if day_check == 'Tuesday':
                check = 1
            if day_check == 'Wednesday':
                check = 2
            if day_check == 'Thursday':
                check = 3
            if day_check == 'Friday':
                check = 4
            if day_check == 'Saturday':
                check = 5
            if day_check == 'Sunday':
                check = 6
            plan = self.env['hr.contract.history'].search(
                [('employee_id', '=', i.id)])
            plan = plan.resource_calendar_id
            plan_day_name = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', self.shift_id.id), ('dayofweek', '=', check)])
            if not plan_day_name:
                shift = 'No Shift Assign'
                status = 'No Shift Assign'
                check_in = "No Shift Assign"
                check_out = "No Shift Assign"
            for rec in plan_day_name:
                # stuff.plan_date_only = rec.new_date
                planned_time = rec.hour_from
                planned_exit_time = rec.hour_to
                shift = str(rec.hour_from) + ' ' +'-'+' '  + str(rec.hour_to)
            if leave:
                status = 'Leave Day'
                check_in = "Leave Day"
                check_out = "Leave Day"
            if day_check == 'Sunday':
                status = 'Rest Day'
                check_in = "Rest Day"
                check_out = "Rest Day"
            # if leave_global:
            #     status = "Global Leave Day"
            #     check_in = "Global Leave Day"
            #     check_out = "Global Leave Day"
            #     shift_name = "Global Leave Day"
            # if shift_name == "No Shift Assigned":
            #     check_in = "Rest Day"
            #     check_out = "Rest Day"
            #     status = "Rest Day"
            if leave:
                datas.append({
                    'code': i.barcode,
                    'name': i.name,
                    'job_id': i.job_id.name,
                    'department_id': i.department_id.name,
                    'shift': shift,
                    'check_in': check_in,
                    'check_out': check_out,

                    'late_arrival': late_arrival,
                    'early_depart': early_depart,
                    'status': status,
                })
        select_companies = self.env['res.company'].browse(self._context.get('allowed_company_ids'))
        select_companies = select_companies[0]
        res = {
            'employee_rec': employee,
            'attendances': datas,
            'reporting': reporting,
            'start_date': self.from_date,
            'end_date': self.to_date,
            'com':select_companies.name

        }
        data = {
            'form': res,
        }
        return self.env.ref('kaytex_present_absent_report.report_hr_attendance_test').report_action([], data=data)
