from datetime import datetime
import pytz
from odoo import api, fields, models,_
from odoo.exceptions import AccessDenied
from datetime import datetime, time, timedelta
from odoo.exceptions import UserError, ValidationError, MissingError

class ApprovalPortal(models.Model):
    _inherit = 'hr.advance.salary'

    # @api.model
    # def create_advance_portal(self, values):
    #     if not (self.env.user.employee_id):
    #         raise AccessDenied()
    #     user = self.env.user
    #     self = self.sudo()
    #     if not (values['request_amount']):
    #         return {
    #             'errors': _('All fields are required !')
    #         }
    #
    #     new_format = "%Y-%m-%d %H:%M:%S"
    #     payment_start= values['payment_start_date']
    #     payment_start = datetime.strptime(payment_start, "%Y-%m-%dT%H:%M")
    #     local_tz = self.env.user.tz
    #     local_dt = pytz.timezone(local_tz)
    #     local_dt1 = local_dt.localize(payment_start, is_dst=None)
    #     new_time = local_dt1.astimezone(pytz.utc)
    #     new_time = new_time.strftime(new_format)
    #
    #     values = {
    #         'request_amount': values['request_amount'],
    #         'payment': values['payment'],
    #         'payment_start_date': new_time,
    #         'reason': values['reason']
    #     }
    #     print(values)
    #     tmp_request = self.env['hr.advance.salary'].sudo().new(values)
    #     # print('True')
    #     values = tmp_request._convert_to_write(tmp_request._cache)
    #     myrequest = self.env['hr.advance.salary'].sudo().create(values)
    #     print(myrequest)
    #     # myrequest.action_ask_approval()
    #     print('This is working')
    #     return {
    #         'id': myrequest.id
    #     }

    def update_advance_portal(self, values):
        start_date = values['date']
        new_format = "%Y-%m-%d %H:%M:%S"
        local_tz = self.env.user.tz
        local_dt = pytz.timezone(local_tz)
        if start_date:
            upd_date_time = datetime.strptime(start_date, "%Y-%m-%dT%H:%M")
            local_dt1 = local_dt.localize(upd_date_time, is_dst=None)
            new_date = local_dt1.astimezone(pytz.utc)
            start_date = new_date.strftime(new_format)

        for advance_rec in self:
            advance_values = {
                'request_amount': values['request_amount'],
                'payment_start_date': start_date,
            }
            print(advance_values)
            print(advance_rec)
            if values['advanceID']:
                adjust_rec = self.env['hr.advance.salary'].sudo().browse(values['advanceID'])
                if adjust_rec:
                    print(values['request_amount'])
                    if adjust_rec.max_loan < float(values['request_amount']):
                        raise ValidationError(
                            f" You can get max {adjust_rec.max_loan} loan/advance")

                    adjust_rec.sudo().write(advance_values)




