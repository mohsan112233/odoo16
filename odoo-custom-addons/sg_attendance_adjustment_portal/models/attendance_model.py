import random
import pytz
from odoo import api, fields, models,_
from datetime import datetime, time, timedelta
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

from odoo.exceptions import AccessDenied


class EmpPortalAttendance(models.Model):
    _inherit = "attendance.adjustment"

    def update_attendance_portal(self, values):
        up_cin = values['check_in']
        up_out = values['check_out']
        new_format = "%Y-%m-%d %H:%M:%S"
        local_tz = self.env.user.tz
        local_dt = pytz.timezone(local_tz)
        if up_cin:
            upd_checkin_time = datetime.strptime(up_cin, "%Y-%m-%dT%H:%M")
            local_dt1 = local_dt.localize(upd_checkin_time, is_dst=None)
            cin = local_dt1.astimezone(pytz.utc)
            up_cin = cin.strftime(new_format)
        if up_out:
            upd_checkout_time = datetime.strptime(up_out, "%Y-%m-%dT%H:%M")
            local_dt2 = local_dt.localize(upd_checkout_time, is_dst=None)
            out = local_dt2.astimezone(pytz.utc)
            up_out = out.strftime(new_format)

        for attendance_rec in self:
            adjust_values = {
                'notes': values['description'],
                'emp_check_in': up_cin,
                'emp_check_out': up_out,
            }
            if values['adjustID']:
                adjust_rec = self.env['attendance.adjustment'].sudo().browse(values['adjustID'])
                if adjust_rec:
                    adjust_rec.sudo().write(adjust_values)

    # @api.model
    # def create_adjustment_portal(self, values):
    #     if not (self.env.user.employee_id):
    #         raise AccessDenied()
    #     user = self.env.user
    #     self = self.sudo()
    #     if not (values['check_in'] and values['check_out']):
    #         return {
    #             'errors': _('All fields are required !')
    #         }
    #     # Final Code
    #     new_format = "%Y-%m-%d %H:%M:%S"
    #     create_check_in = values['check_in']
    #     create_check_out = values['check_out']
    #     checkin_time = datetime.strptime(create_check_in, "%Y-%m-%dT%H:%M")
    #     checkout_time = datetime.strptime(create_check_out, "%Y-%m-%dT%H:%M")
    #     local_tz = self.env.user.tz
    #     local_dt = pytz.timezone(local_tz)
    #     local_dt1 = local_dt.localize(checkin_time, is_dst=None)
    #     local_dt2 = local_dt.localize(checkout_time, is_dst=None)
    #     cin = local_dt1.astimezone(pytz.utc)
    #     cin = cin.strftime(new_format)
    #     out = local_dt2.astimezone(pytz.utc)
    #     out = out.strftime(new_format)
    #
    #     values = {
    #         'notes': values['description'],
    #         'emp_check_in': cin,
    #         'emp_check_out': out,
    #     }
    #     tmp_request = self.env['attendance.adjustment'].sudo().new(values)
    #     # print('True')
    #     values  = tmp_request._convert_to_write(tmp_request._cache)
    #     myrequest = self.env['attendance.adjustment'].sudo().create(values)
    #     myrequest.action_ask_approval()
    #     print('True')
    #     return {
    #         'id': myrequest.id
    #     }



