import pytz
from odoo import http
from odoo.http import request
from datetime import datetime, timezone
import base64
from base64 import b64encode

# This is for inherit controller of another module
# from odoo.odoo import SUPERUSER_ID
# from odoo.exceptions import AccessError, MissingError
# from odoo import fields, _
# from odoo.tools import consteq
# from odoo.odoo.osv import expression
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import logging

_logger = logging.getLogger(__name__)


class AttendanceAPIPortal(CustomerPortal):
    # json for get attendance
    @http.route('/employee_all', type='json', auth='public')
    def get_employee(self):
        try:
            print("Employee")
            user = request.env.user
            Hremployee = request.env['hr.employee']
            # employee_rec = Hremployee.sudo().search([('user_id', '=', user.id)])
            employee_rec = Hremployee.sudo().search([])
            print(employee_rec, 'employeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
            employee = []
            for rec in employee_rec:
                print(rec)
                vals = {
                    'id': rec.id,
                    'employee_name': rec.name,
                    'id_card_no': rec.identification_id,
                    'badge': rec.barcode,
                    'department': rec.department_id.name,
                    'designation': rec.job_id.name,
                }
                print(vals)
                employee.append(vals)
            print("Employee", employee)
            records = {'status': 200, 'response': employee, 'message': 'All Employee Details fetched'}
            return records
        except:
            return {
                'success': False, 'message': 'Unable to get Employee Details'
            }

    @http.route('/new_attendance_record', type='json', auth='user')
    def new_attend_record(self, **rec):
        try:
            new_format = "%Y-%m-%d %H:%M:%S"
            local_tz = request.env.user.tz
            local_dt = pytz.timezone(local_tz)

            if request:
                # user = request.env.user
                # mob_checkin_date = datetime.today()
                # mob_checkin = datetime.now()
                user = int(rec['user_id'])
                att_time = rec['att_time']
                att_date = rec['att_date']
                device_id = int(rec['device_id'])
                device_name = rec['device_name']
                verify_mode = int(rec['verify_mode'])
                att_mode = int(rec['att_mode'])

                # print(mob_checkin,mob_checkin_date)
                # if mob_checkin:
                #     print(mob_checkin)
                #     upd_checkin_time = datetime.strptime(mob_checkin, "%Y-%m-%dT%H:%M")
                #     print(upd_checkin_time)
                #     local_dt1 = local_dt.localize(upd_checkin_time, is_dst=None)
                #     cin = local_dt1.astimezone(pytz.utc)
                #     mob_checkin = mob_checkin.strftime(new_format)
                #     print(mob_checkin)
                # if mob_checkin_date:
                #     upd_checkin_time = datetime.strptime(mob_checkin_date, "%Y-%m-%d")
                #     local_dt1 = local_dt.localize(upd_checkin_time, is_dst=None)
                #     cin = local_dt1.astimezone(pytz.utc)
                #     mob_checkin_date = mob_checkin_date.strftime("%Y-%m-%d")

                # if mob_checkout:
                #     upd_checkout_time = datetime.strptime(mob_checkout, "%Y-%m-%dT%H:%M")
                #     local_dt2 = local_dt.localize(upd_checkout_time, is_dst=None)
                #     cout = local_dt2.astimezone(pytz.utc)
                #     mob_checkout = cout.strftime(new_format)
                # print(mob_checkin)
                # print(mob_checkout)

                if user:
                    vals = {
                        'user_id': user,
                        'att_time': datetime.fromtimestamp(int(att_time)).strftime('%Y-%m-%d %H:%M:%S'),
                        'att_date': datetime.fromtimestamp(int(att_date)).strftime("%Y-%m-%d"),
                        'device_id': device_id,
                        'device_name': device_name,
                        'verify_mode': verify_mode,
                        'att_mode': att_mode,
                    }
                    print(vals)
                    new_record = request.env['draft.attendance'].sudo(True).create(vals)

                    args = {
                        'success': True, 'message': 'Mark Attendance successfully', 'id': new_record.id
                    }
            return args
        except:
            return {
                'success': False, 'message': 'Unable to Mark Attendance'
            }
            # raise werkzeug.exceptions.BadRequest("Request cannot be made right now")
