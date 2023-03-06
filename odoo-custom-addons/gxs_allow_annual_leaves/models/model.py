from odoo import models, fields, api
from odoo.exceptions import UserError
import datetime
from datetime import date, datetime, time, timedelta
from datetime import date
from dateutil.relativedelta import relativedelta
class AnnualLeaves(models.Model):
    _inherit = 'hr.leave'
    from_date = fields.Date('From Date', default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
                            required=True)
    to_date = fields.Date("To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    def action_approve(self):
        print(self.from_date.strftime('%Y-07-01'))
        from_1st_jun = self.from_date.strftime('%Y-07-01')
        today_month = date.today().month
        for emp in self.employee_id:
            print('hi',self.holiday_status_id.name)
            # if self.holiday_status_id.name == 'Annual Leave':

            annual_leave = self.env['hr.leave.allocation'].search(['&',('holiday_status_id','=',self.holiday_status_id.name)
            ,('employee_id.id','=',emp.id)],limit=1, order='id desc')
            print(annual_leave)

            total_annal = annual_leave.number_of_days_display
            pr_month = total_annal/12
            today_month = int(today_month)
            if int(today_month) > 6:
                today_month = today_month - 6
                pr_month = pr_month * int(today_month)
                print(pr_month)
                count = 0
            else:
                today_month = today_month + 6
                pr_month = pr_month * int(today_month)
                print(pr_month)
            #
            # print(pr_month,'test1')
            # pr_month = pr_month * int(today_month)
            # print(pr_month, 'test2')
            count = 0
            annual_leaves = self.env['hr.leave'].search(
                [('employee_id.id', '=',emp.id), ('request_date_from', '>=', from_1st_jun),
                 ('request_date_from', '<=', self.to_date), ('state', '=', 'validate'),
                 ('holiday_status_id', '=', self.holiday_status_id.name)])
            for i in annual_leaves:
                count = count + i.number_of_days
            pr_month = pr_month - count
            print(pr_month,'test0',count)
            if self.number_of_days > pr_month:
                raise UserError((f'{emp.name} can get  maximum {pr_month} {self.holiday_status_id.name} '))
            else:
                change_leave = self.env['hr.leave.allocation'].search(
                    ['&', ('holiday_status_id', '=', self.holiday_status_id.name)
                        , ('employee_id.id', '=', emp.id)], limit=1, order='id desc')
                change_leave.write({
                    'count_allow_leaves': pr_month-self.number_of_days,

                })
                super(AnnualLeaves, self).action_approve()
        # else:
        #     super(AnnualLeaves, self).action_approve()
class HrLeaveReport(models.Model):
    _inherit = 'hr.leave.allocation'
    count_allow_leaves = fields.Float(string='Allow leaves')
    def count_leaves_leaves_action(self):
        print('worked')
        today_month = date.today().month
        for n in range(2):
            print(n)
            if n == 0:
                get_days_all_request = self.env['hr.leave.allocation'].search([('date_to', '>=', date.today()),('state', '=', 'validate')
                                                                            ])
            else:
                get_days_all_request = self.env['hr.leave.allocation'].search([
                                                                               ('date_to', '=', False),('state', '=', 'validate')])
            print(n,get_days_all_request)
            for emp in get_days_all_request:
                total_annal = emp.number_of_days_display
                print(total_annal)
                pr_month = total_annal/12
                print(pr_month)
                today_month = int(today_month)
                if int(today_month) > 6:
                    today_month = today_month - 6
                    pr_month = pr_month * int(today_month)
                    print(pr_month)
                    count = 0
                else:
                    today_month = today_month + 6
                    pr_month = pr_month * int(today_month)
                    print(pr_month)
                pr_month = pr_month - emp.leaves_taken
                print(pr_month,emp.leaves_taken)
                emp.write({
                    'count_allow_leaves': round(pr_month,2)

                })