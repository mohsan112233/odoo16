from datetime import datetime
import pytz
from odoo import api, fields, models,_
from odoo.exceptions import AccessDenied
from datetime import datetime, time, timedelta


class SkipPortal(models.Model):
    _inherit = 'hr.skip.installment'

    # @api.model
    # def create_skip_portal(self, values):
    #     if not (self.env.user.employee_id):
    #         raise AccessDenied()
    #     user = self.env.user
    #     self = self.sudo()
    #     if not (values['date']):
    #         return {
    #             'errors': _('All fields are required !')
    #         }
    #
    #     print('hello')
    #     new_format = "%Y-%m-%d %H:%M:%S"
    #     payment_start = values['date']
    #     payment_start = datetime.strptime(payment_start, "%Y-%m-%dT%H:%M")
    #     local_tz = self.env.user.tz
    #     local_dt = pytz.timezone(local_tz)
    #     local_dt1 = local_dt.localize(payment_start, is_dst=None)
    #     new_time = local_dt1.astimezone(pytz.utc)
    #     new_time = new_time.strftime(new_format)
    #
    #     values = {
    #         'advance_salary_id': values['advance_salary_id'],
    #         'date': new_time,
    #         'name': values['name']
    #     }
    #     print(values)
    #     tmp_request = self.env['hr.skip.installment'].sudo().new(values)
    #     # print('True')
    #     values = tmp_request._convert_to_write(tmp_request._cache)
    #     myrequest = self.env['hr.skip.installment'].sudo().create(values)
    #     print(myrequest)
    #     # myrequest.action_ask_approval()
    #     print('True')
    #     return {
    #         'id': myrequest.id
    #     }

    def update_skip_portal(self, values):
        # date = values['date']
        # new_format = "%Y-%m-%d %H:%M:%S"
        # local_tz = self.env.user.tz
        # local_dt = pytz.timezone(local_tz)
        # if date:
        #     upd_date_time = datetime.strptime(date, "%Y-%m-%dT%H:%M")
        #     local_dt1 = local_dt.localize(upd_date_time, is_dst=None)
        #     new_date = local_dt1.astimezone(pytz.utc)
        #     date = new_date.strftime(new_format)

        for skip_rec in self:
            skip_values = {
                'name': values['name'],
                'date': values['date'],
                # 'date': date,
            }
            print(skip_values)
            print(skip_rec)
            if values['skipID']:
                adjust_rec = self.env['hr.skip.installment'].sudo().browse(values['skipID'])
                if adjust_rec:
                    adjust_rec.sudo().write(skip_values)




