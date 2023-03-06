from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError, MissingError
from datetime import datetime, time, timedelta, date
import time as ti
import pytz
import calendar

from pytz import timezone


class AttendanceInherit(models.Model):
    _inherit = 'hr.attendance'
    # check_in = fields.Datetime(string="Check In", default=False, required=True)
    # employee_id = fields.Many2one('hr.employee', string="Employee",default=False, required=True, ondelete='cascade', index=True)

    from_date = fields.Date('From Date', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    to_date = fields.Date("To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    mint_15 = fields.Datetime(string='15')
    # plan_date_only = fields.Date('Planned Date', compute='_plan_attendance', store=True)
    planned_date = fields.Datetime('Planned Checkin', compute='_plan_attendance', store=True)
    planned_time = fields.Float('Planned Time', compute='_plan_attendance', store=True)
    planned_exit_time = fields.Float('Planned Checkout', compute='_plan_attendance', store=True)
    checkin_date = fields.Date('Date-Checkin', compute='_get_new_current_checkin', store=True, default=False)
    # checkout_date = fields.Date('Date-Checkout', compute='_get_new_current_checkout', store=True, default=False)
    late_emp = fields.Float('Late', compute="_late_emp_hours", store=True)
    overtime = fields.Float('Overtime', compute='_overtime_emp_hour', store=True)
    assumption_request = fields.Char(string='Assumption Request', readonly=True)

    @api.depends('check_in')
    def _get_new_current_checkin(self):
        for rec in self:
            if rec.check_in:
                date = datetime.strftime(rec.check_in, '%Y-%m-%d %H:%M:%S')
                new_checkin = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
                # print(new_checkin)
                rec.checkin_date = new_checkin

    #
    # @api.depends('check_out')
    # def _get_new_current_checkout(self):
    #     for rec in self:
    #         if rec.check_out:
    #             date = datetime.strftime(rec.check_out, '%Y-%m-%d %H:%M:%S')
    #             new_checkout = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
    #             # print(new_checkin)
    #             rec.checkout_date = new_checkout
    # 
    @api.depends('check_in')
    def _plan_attendance(self):
        for stuff in self:
            date_day = stuff.check_in.date()
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
                [('employee_id', '=', stuff.employee_id.id)])
            plan = plan.resource_calendar_id
            plan_day_name = self.env['resource.calendar.attendance'].search(
                [('calendar_id', '=', plan.id), ('dayofweek', '=', check)])

            for rec in plan_day_name:
                # stuff.plan_date_only = rec.new_date
                print(rec.hour_from)
                stuff.planned_time = rec.hour_from
                stuff.planned_exit_time = rec.hour_to

    @api.constrains('check_in')
    def _late_emp_hours(self):
        for rec in self:
            if rec.check_in:
                # pay_slip = self.env['hr.payslip'].search(
                #     ['&', ('employee_id', '=', rec.employee_id.id), ('state', '=', 'verify')])
                # total_days =  pay_slip.date_to - pay_slip.date_from
                #
                # try:
                #     total_days = total_days.total_seconds() / 3600
                #     total_days = total_days/24
                # except:
                #     raise ValidationError(f"{rec.employee_id.name} Has no Payslip please! create Payslip First")

                # late_detuct_salary = 0
                # for i in pay_slip.line_ids:
                #     if i.name == 'Late deduct':
                #         late_detuct_salary = i.amount
                #         print('-------------',late_detuct_salary)
                #         late_detuct_salary = -(late_detuct_salary)
                #         print('+++++++++++++',late_detuct_salary)
                #         break
                # net_selary = pay_slip.line_ids[-1].amount - late_detuct_salary
                # per_day_salary = net_selary/total_days
                rec.mint_15 = datetime.strftime(rec.check_in, '%Y-%m-%d 02:15:00')

                planned_time_str = str(rec.planned_time)
                planned_time_list = list(planned_time_str)
                h = 0

                for i in planned_time_str:
                    h = h + 1
                    if i == '.':
                        hour = planned_time_str[0:h - 1]
                        if len(hour) == 1:
                            hour = '0' + hour

                        mints = planned_time_str[h:]
                        if len(mints) == 1:
                            mints = '0' + mints

                        rec.mint_15 = datetime.strftime(rec.check_in, f'%Y-%m-%d {hour}:{mints}:%S')

                # get_mint_15_up = rec.planned_time - rec.mint_15
                # rec.mint_15 = datetime.strftime(rec.check_in, '%Y-%m-%d 00:00:00')
                # get_only_time_from_pland = rec.planned_date - rec.mint_15
                # get_15_mint = get_only_time_from_pland - get_mint_15_up
                check_in = rec.check_in
                check_in = check_in.astimezone(pytz.timezone('Asia/Karachi'))
                check_in_hour = check_in.strftime('%H')
                check_in = check_in.strftime('%Y-%m-%d %H:%M:%S')
                check_in = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')

                # check_in = check_in.strptime('%Y-%m-%d %H:%M:%S')
                # check_in = datetime.strftime(check_in,'%Y-%m-%d %H:%M:%S')

                get_hour = check_in - rec.mint_15

                # final_time = get_hour - get_15_mint
                rec.late_emp = get_hour.total_seconds() / 3600
                if rec.late_emp > 0:
                    relax_time = self.env['kt.atten.policy'].search(
                        [])
                    relax_time = relax_time.time
                    print('1', relax_time)
                    relax_time = (relax_time / 100) * 100
                    print('2', relax_time)
                    # relax_time = relax_time / 100
                    # print('3',relax_time)
                    rec.late_emp = rec.late_emp - relax_time

                    # relax_time = self.env['ir.config_parameter'].sudo().get_param("relax_time")
                    #  relax_time = int(relax_time)
                    #  relax_time = (relax_time/60)*100
                    #  relax_time = relax_time/100
                    #  rec.late_emp = rec.late_emp - relax_time
                    if rec.late_emp < 0:
                        rec.late_emp = 0

                if rec.check_out:
                    work_hours = rec.check_out - rec.check_in
                    rec.worked_hours = work_hours.total_seconds() / 3600.0

                if rec.late_emp > 0.0:

                    count_late = self.env["hr.attendance"].search_count(
                        [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', rec.from_date),
                         ('check_in', '!=', False), ('late_emp', '>', 0.0),
                         ('checkin_date', '<=', rec.to_date)
                         ])

                    duplicate = self.env["hr.leave"].search(
                        [('employee_id', '=', rec.employee_id.id), ('name', '=', 'Late Deduction'),('date_from', '=', rec.check_in.date()),
                         ])
                    if not duplicate:
                        print('work', count_late, rec.late_emp,'nnnnnnnnnnnnnnnnnnnnm',duplicate)
                        date_day = rec.check_in.date()
                        list_leave_type = ['Casual Leave', 'Sick Leave', 'Annual Leave','Short leave']
                        # list_leave_type = ['Short leave']
                        for type in list_leave_type:
                            #
                            leave_by_type = self.env['hr.leave.allocation'].search(
                                ['&', ('holiday_status_id', '=', type), ('employee_id.id', '=', rec.employee_id.id)],
                                limit=1, order='id desc')

                            date_leave_alocation = leave_by_type.date_from
                            allocate_leaves = 'not allow'
                            if leave_by_type.date_from:
                                if leave_by_type.date_from <= date_day:
                                    allocate_leaves = 'allow'
                            causal_leave = self.env["hr.leave"].search(
                                [('employee_id', '=', rec.employee_id.id), ('date_from', '>=', date_leave_alocation),
                                 ('state', '=', 'validate')
                                    , ('holiday_status_id', '=', type)
                                 ])
                            duration = 0
                            for i in causal_leave:
                                duration = duration + i.number_of_days
                            total_leave = leave_by_type.number_of_days_display - duration
                            if type == 'Short leave':
                                total_leave = 10
                            print("total_leave", total_leave)
                            leave_id = self.env['hr.leave.type'].search(
                                [('name', '=', type),('company_id','=',rec.employee_id.company_id.id)])
                            duplicate = self.env["hr.leave"].search_count(
                                [('employee_id', '=', rec.employee_id.id), ('name', '=', 'Late Deduction'),('date_from', '=', date_day),
                                 ])
                            late_check_in = self.env['late.check_in'].search(
                                ['&', ('employee_id', '=', rec.employee_id.id), ('description','ilike','Late'),('date', '=', rec.check_in.date())])
                            # print(duplicate,';;;;;')
                            # count_late = self.env["hr.attendance"].search_count(
                            #     [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', rec.from_date),
                            #      ('check_in', '!=', False), ('late_emp', '>', 0),
                            #      ('checkin_date', '<=', rec.to_date), ('assumption_request', '=', False)
                            #      ])

                            if rec.late_emp <= 4 and rec.late_emp >= 2 and total_leave >= 0.5:
                                if late_check_in:
                                    late_check_in.unlink()
                                id = self.env['hr.leave'].create({
                                    'employee_id': rec.employee_id.id,
                                    'date_from': date_day,
                                    'date_to': date_day,
                                    'request_date_from': date_day,
                                    'request_date_to': date_day,
                                    'holiday_status_id': leave_id.id,
                                    'number_of_days': 0.5,
                                    'name': 'Late Deduction',

                                })

                                # half_day_salary = per_day_salary / .5
                                self.env['late.check_in'].create({
                                    'employee_id': rec.employee_id.id,
                                    'late_minutes': rec.late_emp,
                                    'date': rec.check_in.date(),
                                    'attendance_id': rec.id,
                                    'amount': 0.5,
                                    'description': f'Late Deduct from leave {leave_id.name}',
                                })
                                print('/..............work')
                                #id.action_validate()
                                break

                            elif rec.late_emp <= 2 and total_leave >= 0.25:
                                if late_check_in:
                                    late_check_in.unlink()

                                id = self.env['hr.leave'].create({
                                    'employee_id': rec.employee_id.id,
                                    'date_from': date_day,
                                    'date_to': date_day,
                                    'request_date_from': date_day,
                                    'request_date_to': date_day,
                                    'holiday_status_id': leave_id.id,
                                    'number_of_days': 0.25,
                                    'name': 'Late Deduction',

                                })

                                # half_day_salary = per_day_salary / .25
                                self.env['late.check_in'].sudo().create({
                                    'employee_id': rec.employee_id.id,
                                    'late_minutes': rec.late_emp,
                                    'date': rec.check_in.date(),
                                    'attendance_id': rec.id,
                                    'amount': 0.25,
                                    'description': f'Late Deduct from {leave_id.name}',
                                })
                                print('/..............work')
                                #id.action_validate()
                                break

                            elif rec.late_emp > 4 and total_leave >= 1:
                                if late_check_in:
                                    late_check_in.unlink()
                                print(type,leave_id)
                                id = self.env['hr.leave'].create({
                                    'employee_id': rec.employee_id.id,
                                    'date_from': date_day,
                                    'date_to': date_day,
                                    'request_date_from': date_day,
                                    'request_date_to': date_day,
                                    'holiday_status_id': leave_id.id,
                                    'number_of_days': 1,
                                    'name': 'Late Deduction',

                                })
                                # half_day_salary = per_day_salary / .5
                                self.env['late.check_in'].sudo().create({
                                    'employee_id': rec.employee_id.id,
                                    'late_minutes': rec.late_emp,
                                    'date': rec.check_in.date(),
                                    'attendance_id': rec.id,
                                    'amount': 1,
                                    'description': f'Late Deduct from {leave_id.name}',
                                })
                                print('/..............work')
                                #id.action_validate()
                                break
                        #
                        leave_id = self.env['hr.leave.type'].search(
                            [('name', '=', 'Short leave'),('company_id','=',rec.employee_id.company_id.id)])
                        late_check_in = self.env['late.check_in'].search(
                            ['&', ('employee_id', '=', rec.employee_id.id), ('description','ilike','Late'),('date', '=', rec.check_in.date())])
                        # print(late_check_in,"late_check_in")
                        count_late = self.env["hr.attendance"].search_count(
                            [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', rec.from_date),
                             ('check_in', '!=', False), ('late_emp', '>', 0),
                             ('checkin_date', '<=', rec.to_date)
                             ])
                        duplicate = self.env["hr.leave"].search_count(
                            [('employee_id', '=', rec.employee_id.id), ('date_from', '=', date_day),
                             ('name', '=', 'Late Deduction')
                             ])
                        if rec.late_emp <= 4 and rec.late_emp >= 2 and not duplicate:
                            if late_check_in:
                                late_check_in.unlink()

                            # half_day_salary = per_day_salary / .5
                            self.env['late.check_in'].sudo().create({
                                'employee_id': rec.employee_id.id,
                                'late_minutes': rec.late_emp,
                                'date': rec.check_in.date(),
                                'attendance_id': rec.id,
                                'amount': 0.5,
                                'description': 'Late Deduction from salary',

                            })
                            id = self.env['hr.leave'].create({
                                'employee_id': rec.employee_id.id,
                                'date_from': date_day,
                                'date_to': date_day,
                                'request_date_from': date_day,
                                'request_date_to': date_day,
                                'holiday_status_id': leave_id.id,
                                'number_of_days': 0.5,
                                'name': 'Late Deduction',

                            })
                            #id.action_validate()

                        elif rec.late_emp <= 2 and not duplicate:
                            if late_check_in:
                                late_check_in.unlink()

                            # half_day_salary = per_day_salary / .25
                            self.env['late.check_in'].sudo().create({
                                'employee_id': rec.employee_id.id,
                                'late_minutes': rec.late_emp,
                                'date': rec.check_in.date(),
                                'attendance_id': rec.id,
                                'amount': 0.25,
                                'description': 'Late Deduction from salary',
                            })

                            id = self.env['hr.leave'].create({
                                'employee_id': rec.employee_id.id,
                                'date_from': date_day,
                                'date_to': date_day,
                                'request_date_from': date_day,
                                'request_date_to': date_day,
                                'holiday_status_id': leave_id.id,
                                'number_of_days': 0.25,
                                'name': 'Late Deduction',

                            })
                            #id.action_validate()
                        elif rec.late_emp > 4 and not duplicate:
                            if late_check_in:
                                late_check_in.unlink()

                            # half_day_salary = per_day_salary / 1
                            self.env['late.check_in'].sudo().create({
                                'employee_id': rec.employee_id.id,
                                'late_minutes': rec.late_emp,
                                'date': rec.check_in.date(),
                                'attendance_id': rec.id,
                                'amount': 1,
                                'description': 'Late Deduction from salary',
                            })

                            id = self.env['hr.leave'].create({
                                'employee_id': rec.employee_id.id,
                                'date_from': date_day,
                                'date_to': date_day,
                                'request_date_from': date_day,
                                'request_date_to': date_day,
                                'holiday_status_id': leave_id.id,
                                'number_of_days': 1,
                                'name': 'Late Deduction',

                            })
                            #id.action_validate()

                elif rec.late_emp > 0:
                    if rec.late_emp < 0:
                        rec.late_emp = 0

                # check_in_hour = check_in_hour.strftime('%H')
            else:

                rec.late_emp = False

    @api.depends('check_out')
    def _overtime_emp_hour(self):
        for rec in self:
            last_month_day = rec.check_in.date().replace(day=calendar.monthrange(rec.check_in.date().year, rec.check_in.date().month)[1])
            date_from = rec.check_in.date().replace(day=1)
            date_day = rec.check_in.date()
            if rec.check_out:
                permanent = self.env["hr.contract.history"].search(
                    [('employee_id', '=', rec.employee_id.id)
                     ])
                state = 0
                for i in permanent.contract_ids:
                    if i.state == 'open':
                        state = i.per_hour
                if rec.planned_exit_time:
                    check_out = rec.check_out
                    check_out = check_out.astimezone(pytz.timezone('Asia/Karachi'))
                    # check_in_hour = check_in.strftime('%H')
                    check_out = check_out.strftime('%Y-%m-%d %H:%M:%S')
                    check_out = datetime.strptime(check_out, '%Y-%m-%d %H:%M:%S')
                    planned_exit_time_str = str(rec.planned_exit_time)

                    h = 0
                    s = 0
                    for i in planned_exit_time_str:
                        h = h + 1
                        if i == '.':
                            hour = planned_exit_time_str[0:h - 1]
                            if len(hour) == 1:
                                hour = '0' + hour

                            mints = planned_exit_time_str[h:]
                            if len(mints) == 1:
                                mints = '0' + mints

                            rec.mint_15 = datetime.strftime(rec.check_out, f'%Y-%m-%d {hour}:{mints}:%S')

                    start_dt = fields.Datetime.from_string(check_out)
                    finish_dt = fields.Datetime.from_string(rec.mint_15)
                    over_hour = start_dt - finish_dt
                    rec.overtime = over_hour.total_seconds() / 3600.0
                    work_hours = rec.check_out - rec.check_in
                    rec.worked_hours = work_hours.total_seconds() / 3600.0
                    overtime = self.env['hr.overtime.calculate.abc']
                    if rec.overtime < 0.0:
                        count_early_leave = abs(rec.overtime)
                        count_late = self.env["hr.attendance"].search_count(
                            [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', rec.from_date),
                             ('check_in', '!=', False), ('late_emp', '>', 0.0),
                             ('checkin_date', '<=', rec.to_date)
                             ])

                        duplicate = self.env["hr.leave"].search(
                            [ ('name', '=', 'Early Leave Deduction'),('employee_id', '=', rec.employee_id.id), ('date_from', '=', rec.check_in.date()),
                             ])
                        if not duplicate:
                            print('work', count_late, rec.late_emp, 'nnnnnnnnnnnnnnnnnnnnm', duplicate)
                            date_day = rec.check_in.date()
                            list_leave_type = ['Casual Leave', 'Sick Leave', 'Annual Leave', 'Short leave']
                            # list_leave_type = ['Short leave']
                            for type in list_leave_type:
                                #
                                leave_by_type = self.env['hr.leave.allocation'].search(
                                    ['&', ('holiday_status_id', '=', type),
                                     ('employee_id.id', '=', rec.employee_id.id)],
                                    limit=1, order='id desc')

                                date_leave_alocation = leave_by_type.date_from
                                allocate_leaves = 'not allow'
                                if leave_by_type.date_from:
                                    if leave_by_type.date_from <= date_day:
                                        allocate_leaves = 'allow'
                                causal_leave = self.env["hr.leave"].search(
                                    [('employee_id', '=', rec.employee_id.id),
                                     ('date_from', '>=', date_leave_alocation),
                                     ('state', '=', 'validate')
                                        , ('holiday_status_id', '=', type)
                                     ])
                                duration = 0
                                for i in causal_leave:
                                    duration = duration + i.number_of_days
                                total_leave = leave_by_type.number_of_days_display - duration
                                if type == 'Short leave':
                                    total_leave = 10
                                print("total_leave", total_leave)
                                leave_id = self.env['hr.leave.type'].search(
                                    [('name', '=', type),('company_id','=',rec.employee_id.company_id.id)])
                                duplicate = self.env["hr.leave"].search_count(
                                    [('employee_id', '=', rec.employee_id.id), ('date_from', '=', date_day), ('name', '=', 'Early Leave Deduction')
                                     ])
                                late_check_in = self.env['late.check_in'].search(
                                    ['&', ('employee_id', '=', rec.employee_id.id), ('description','ilike','Early Leave'),('date', '=', rec.check_in.date())])
                                # print(duplicate,';;;;;')
                                # count_late = self.env["hr.attendance"].search_count(
                                #     [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', rec.from_date),
                                #      ('check_in', '!=', False), ('late_emp', '>', 0),
                                #      ('checkin_date', '<=', rec.to_date), ('assumption_request', '=', False)
                                #      ])

                                if count_early_leave <= 4 and count_early_leave >= 2 and total_leave >= 0.5:
                                    if late_check_in:
                                        late_check_in.unlink()
                                    id = self.env['hr.leave'].create({
                                        'employee_id': rec.employee_id.id,
                                        'date_from': date_day,
                                        'date_to': date_day,
                                        'request_date_from': date_day,
                                        'request_date_to': date_day,
                                        'holiday_status_id': leave_id.id,
                                        'number_of_days': 0.5,
                                        'name': 'Early Leave Deduction',

                                    })

                                    # half_day_salary = per_day_salary / .5
                                    self.env['late.check_in'].create({
                                        'employee_id': rec.employee_id.id,
                                        'late_minutes': rec.late_emp,
                                        'date': rec.check_in.date(),
                                        'attendance_id': rec.id,
                                        'amount': 0.5,
                                        'description': f'Early Leave Deduct from leave {leave_id.name}',
                                    })
                                    print('/..............work')
                                    #id.action_validate()
                                    break

                                elif count_early_leave <= 2 and total_leave >= 0.25:
                                    if late_check_in:
                                        late_check_in.unlink()

                                    id = self.env['hr.leave'].create({
                                        'employee_id': rec.employee_id.id,
                                        'date_from': date_day,
                                        'date_to': date_day,
                                        'request_date_from': date_day,
                                        'request_date_to': date_day,
                                        'holiday_status_id': leave_id.id,
                                        'number_of_days': 0.25,
                                        'name': 'Early Leave Deduction',

                                    })

                                    # half_day_salary = per_day_salary / .25
                                    self.env['late.check_in'].sudo().create({
                                        'employee_id': rec.employee_id.id,
                                        'late_minutes': rec.late_emp,
                                        'date': rec.check_in.date(),
                                        'attendance_id': rec.id,
                                        'amount': 0.25,
                                        'description': f'Early Leave Deduct from {leave_id.name}',
                                    })
                                    print('/..............work')
                                    #id.action_validate()
                                    break

                                elif count_early_leave > 4 and total_leave >= 1:
                                    if late_check_in:
                                        late_check_in.unlink()

                                    id = self.env['hr.leave'].create({
                                        'employee_id': rec.employee_id.id,
                                        'date_from': date_day,
                                        'date_to': date_day,
                                        'request_date_from': date_day,
                                        'request_date_to': date_day,
                                        'holiday_status_id': leave_id.id,
                                        'number_of_days': 1,
                                        'name': 'Early Leave Deduction',

                                    })
                                    # half_day_salary = per_day_salary / .5
                                    self.env['late.check_in'].sudo().create({
                                        'employee_id': rec.employee_id.id,
                                        'late_minutes': rec.late_emp,
                                        'date': rec.check_in.date(),
                                        'attendance_id': rec.id,
                                        'amount': 1,
                                        'description': f'Early Leave Deduct from {leave_id.name}',
                                    })
                                    print('/..............work')
                                    #id.action_validate()
                                    break
                            #
                            leave_id = self.env['hr.leave.type'].search(
                                [('name', '=', 'Short leave'),('company_id','=',rec.employee_id.company_id.id)])
                            late_check_in = self.env['late.check_in'].search(
                                ['&', ('employee_id', '=', rec.employee_id.id), ('description','ilike','Early Leave'),('date', '=', rec.check_in.date())])
                            # print(late_check_in,"late_check_in")
                            count_late = self.env["hr.attendance"].search_count(
                                [('employee_id', '=', rec.employee_id.id), ('checkin_date', '>=', rec.from_date),
                                 ('check_in', '!=', False), ('late_emp', '>', 0),
                                 ('checkin_date', '<=', rec.to_date)
                                 ])
                            duplicate = self.env["hr.leave"].search_count(
                                [('employee_id', '=', rec.employee_id.id), ('date_from', '=', date_day),
                                 ('name', '=', 'Early Leave Deduction')
                                 ])
                            if count_early_leave <= 4 and count_early_leave >= 2 and not duplicate:
                                if late_check_in:
                                    late_check_in.unlink()

                                # half_day_salary = per_day_salary / .5
                                self.env['late.check_in'].sudo().create({
                                    'employee_id': rec.employee_id.id,
                                    'late_minutes': rec.late_emp,
                                    'date': rec.check_in.date(),
                                    'attendance_id': rec.id,
                                    'amount': 0.5,
                                    'description': 'Early Leave Deduction from salary',

                                })
                                id = self.env['hr.leave'].create({
                                    'employee_id': rec.employee_id.id,
                                    'date_from': date_day,
                                    'date_to': date_day,
                                    'request_date_from': date_day,
                                    'request_date_to': date_day,
                                    'holiday_status_id': leave_id.id,
                                    'number_of_days': 0.5,
                                    'name': 'Early Leave Deduction',

                                })
                                #id.action_validate()

                            elif count_early_leave <= 2 and not duplicate:
                                if late_check_in:
                                    late_check_in.unlink()

                                # half_day_salary = per_day_salary / .25
                                self.env['late.check_in'].sudo().create({
                                    'employee_id': rec.employee_id.id,
                                    'late_minutes': rec.late_emp,
                                    'date': rec.check_in.date(),
                                    'attendance_id': rec.id,
                                    'amount': 0.25,
                                    'description': 'Early Leave Deduction from salary',
                                })

                                id = self.env['hr.leave'].create({
                                    'employee_id': rec.employee_id.id,
                                    'date_from': date_day,
                                    'date_to': date_day,
                                    'request_date_from': date_day,
                                    'request_date_to': date_day,
                                    'holiday_status_id': leave_id.id,
                                    'number_of_days': 0.25,
                                    'name': 'Early Leave Deduction',

                                })
                                #id.action_validate()
                            elif count_early_leave > 4 and not duplicate:
                                if late_check_in:
                                    late_check_in.unlink()

                                # half_day_salary = per_day_salary / 1
                                self.env['late.check_in'].sudo().create({
                                    'employee_id': rec.employee_id.id,
                                    'late_minutes': rec.late_emp,
                                    'date': rec.check_in.date(),
                                    'attendance_id': rec.id,
                                    'amount': 1,
                                    'description': 'Early Leave Deduction from salary',
                                })

                                id = self.env['hr.leave'].create({
                                    'employee_id': rec.employee_id.id,
                                    'date_from': date_day,
                                    'date_to': date_day,
                                    'request_date_from': date_day,
                                    'request_date_to': date_day,
                                    'holiday_status_id': leave_id.id,
                                    'number_of_days': 1,
                                    'name': 'Early Leave Deduction',

                                })
                                #id.action_validate()

                    if rec.overtime > 0 and state != 0:
                        lines = overtime.search([
                            ('employee_id', '=', rec.employee_id.id),
                            ('date_from', '<=', date_from),
                            ('date_to', '>=', last_month_day),
                        ])
                        over_time = rec.overtime * 60 / 50
                        if lines:

                            print(rec.overtime, 'overtime', lines.attendance_ids, '1')

                            vals = {
                                'employee_id': rec.employee_id.id,
                                'date': date_day,
                                'attendance_id': rec.id,
                                'overtime_hours': int(over_time),
                                'total_amount_day': int(over_time) * state,
                                'overtime_calculate_id': lines.id,
                            }

                            line_id = self.env['hr.overtime.calculate.lines'].search(
                                [('attendance_id', '=', rec.id), ('overtime_calculate_id', '=', lines.id)])
                            if not line_id and rec.id:
                                self.env['hr.overtime.calculate.lines'].create(vals)
                                total = 0
                                for las in lines.attendance_ids:
                                    total += las.total_amount_day
                                lines.total_amount = total
                            else:
                                line_id.overtime_hours = int(over_time)
                                line_id.total_amount_day = int(over_time) * state
                                total = 0
                                for las in lines.attendance_ids:
                                    total += las.total_amount_day
                                lines.total_amount = total
                        else:
                            print(rec.overtime, lines, '2')
                            line = overtime.create({
                                'employee_id': rec.employee_id.id,
                                'date_from': date_from,
                                'date_to': last_month_day,
                                'total_amount': int(over_time) * state
                            })

                            vals = {
                                'employee_id': rec.employee_id.id,
                                'attendance_id': rec.id,
                                'date': date_day,
                                'overtime_hours': int(over_time),
                                'total_amount_day': int(over_time) * state,
                                'overtime_calculate_id': line.id,
                            }
                            line_id = self.env['hr.overtime.calculate.lines'].search(
                                [('attendance_id', '=', rec.id), ('overtime_calculate_id', '=', line.id)])
                            if not line_id and rec.id:
                                self.env['hr.overtime.calculate.lines'].create(vals)
                            else:
                                line_id.overtime_hours = int(over_time)
                                line_id.total_amount_day = int(over_time) * state
                else:
                    rec.overtime = False





