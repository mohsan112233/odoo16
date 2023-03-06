from werkzeug.exceptions import NotFound
from collections import OrderedDict
import pytz
from odoo import http, _
from odoo.http import request
from datetime import datetime, time, timedelta

# This is for inherit controller of another module
# from odoo.odoo import SUPERUSER_ID
# from odoo.exceptions import AccessError, MissingError
# from odoo import fields, _
# from odoo.tools import consteq
# from odoo.odoo.osv import expression
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import logging

_logger = logging.getLogger(__name__)


class AttendancePortal(CustomerPortal):
    def get_domain_my_attendances(self, user):
        user = request.env.user
        payslip = request.env['hr.attendance']
        payslip_count = payslip.search_count([
            ('employee_id.user_id', '=', [user.id])
        ])

        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        return [
            ('employee_id', '=', emp and emp.id or False),
        ]

    def _prepare_portal_layout_values(self):
        values = super(AttendancePortal, self)._prepare_portal_layout_values()
        user = request.env.user
        attendance = request.env['hr.attendance']
        attendance_count = attendance.search_count([
            ('employee_id.user_id', '=', [user.id]),

        ])
        print(attendance)
        print('First', attendance_count)

        values.update({
            'attendance_count': attendance_count,
        })
        return values

    @http.route(['/employee/attendance/record'], type='http',
                website=True, auth='user')
    def employee_attendances(self, page=1, sortby=None, **kw):
        print('/.,/.,/.,/.,')
        new_format = "%Y-%m-%d %H:%M:%S"
        values = self._prepare_portal_layout_values()
        user = request.env.user
        Hrattendance = request.env['hr.attendance']
        attendance_sudo = request.env['hr.attendance'].sudo()
        # .search([('employee_id.user_id', '=', user.id)])
        domain = self.get_domain_my_attendances(request.env.user)

        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        searchbar_sortings = {
            'create_date': {'label': _('Newest'), 'order': 'create_date desc, id desc'},
            'check_in': {'label': _('Check In'), 'order': 'check_in'},
            'check_out': {'label': _('Check Out'), 'order': 'check_out'},
        }
        if not sortby:
            sortby = 'check_in'
        order = searchbar_sortings[sortby]['order']

        attendance_count = Hrattendance.search_count(domain)

        print(attendance_count)

        # attendances = Hrattendance.sudo().search([('employee_id.user_id', '=', user.id)])
        pager = request.website.pager(
            url="/employee/attendance/record",
            url_args={'sortby': sortby},
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )

        attendances = attendance_sudo.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        lis = []
        for rec in attendances:
            if rec.check_in:
                my_check = rec.check_in
                cin = my_check.astimezone(pytz.timezone('Asia/Karachi'))
                check_in = cin.strftime(new_format)
                print('1', check_in)
            else:
                rec.check_in = False
            if rec.check_out:
                c_out = rec.check_out
                cout = c_out.astimezone(pytz.timezone('Asia/Karachi'))
                check_out = cout.strftime(new_format)
                print('2', check_out)
            val =  {
                'employee_id':  rec.employee_id.name,
                'check_in':  check_in,
                'check_out': check_out,
                'worked_hours': round(rec.worked_hours,2),
             }
            lis.append(val)

        values.update({
            'attendances': lis,
            'pager': pager,
            'page_name': 'attendance',
            'default_url': '/employee/attendance/record',
            # 'order': order,
            # 'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,

        })
        return request.render("sg_attendance_adjustment_portal.attendances_record", values)

    # @http.route('/attendance/form/', type="http", auth="public", website=True)
    # def attendance_form(self, **kw):
    #     # values = self._prepare_portal_layout_values()
    #     user_rec = request.env['hr.employee'].sudo().search([])
    #     # print(user_rec)
    #     # responsible = request.env['res.users'].sudo().search([])
    #
    #     return http.request.render('sg_attendance_adjustment_portal.create_request', {'user_rec': user_rec})

    # # My Task
    # @http.route('/create/attendance/request/', type="http", auth="user", website=True)
    # def create_attendance(self, **kw):
    #     request.env['attendance.adjustment'].sudo().create(kw)
    #     return request.render("sg_attendance_adjustment_portal.employee_thanks", {})

    #
    @http.route(['/employee/attendance/', '/employee/attendance/page/<int:page>'], type='http', website=True, auth='user')
    def view_adjustments(self, page=1, sortby=None, filterby=None, **kw):
        print('.,.,.,.,.,.')
        values = self._prepare_portal_layout_values()
        user = request.env.user
        attend_rec = request.env['attendance.adjustment']
        attendance_sudo = request.env['attendance.adjustment'].sudo()
        domain = self.get_domain_my_attendances(request.env.user)

        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'to_be_approved': {'label': _('Request'), 'domain': [('state', '=', 'to_be_approved')]},
            'approve': {'label': _('Approved'), 'domain': [('state', '=', 'approve')]},
            'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]},
        }

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'emp_check_in': {'label': _('Check In'), 'order': 'emp_check_in'},
        }

        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        attendance_count = attend_rec.search_count(domain)
        print(attendance_count)

        pager = request.website.pager(
            url="/employee/attendance",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )

        attendances = attend_rec.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )

        values.update({
            'attendances': attendances,
            'pager': pager,
            'page_name': 'attendance adjustment',
            'default_url': '/employee/attendance',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'sortby': sortby,
            'filterby': filterby,
        })

        return request.render("sg_attendance_adjustment_portal.attendances", values)

    # adjustment view
    @http.route(['/employee/attendance/<int:attend_id>'], type='http', auth="user", website=True)
    def portal_my_attend_detail(self, attend_id, access_token=None, **kw):
        user = request.env.user
        attendance_sudo = self._document_check_access('attendance.adjustment', attend_id, access_token=access_token)
        values = {
            'attendance_rec': attendance_sudo,
            'token': access_token,
        }
        print(attendance_sudo.id)

        values['pms'] = http.request.env['hr.employee'].search([('id', '=', attendance_sudo.id)])
        print(values)
        return request.render("sg_attendance_adjustment_portal.portal_page_adjustment", values)

    #json for get attendance
    @http.route('/my_attendance', type='json', auth='user')
    def get_attendance(self):
        print("yes its working")
        user = request.env.user
        Hrattendance = request.env['hr.attendance']
        attendance_rec = Hrattendance.sudo().search([('employee_id.user_id', '=', user.id)])
        attendance = []
        for rec in attendance_rec:
            print(round(rec.worked_hours,2),';;;;;')
            vals = {
                'id': rec.id,
                'employee_name': rec.employee_id.name,
                'check_in': rec.check_in,
                'check_out': rec.check_out,
                'worked_hours': round(rec.worked_hours,2)
            }
            attendance.append(vals)
        print("attendance record", attendance)
        data = {'status': 200, 'response': attendance, 'message': 'All attendances fetched'}
        return data

    @http.route('/create_attendance_record', type='json', auth='user')
    def create_attend_record(self, **rec):
        new_format = "%Y-%m-%d %H:%M:%S"
        local_tz = request.env.user.tz
        local_dt = pytz.timezone(local_tz)
        if request.jsonrequest:
            user = request.env.user
            print(user.id)
            mob_checkin = rec['check_in']
            mob_checkout= rec['check_out']
            if mob_checkin:
                upd_checkin_time = datetime.strptime(mob_checkin, "%Y-%m-%dT%H:%M")
                local_dt1 = local_dt.localize(upd_checkin_time, is_dst=None)
                cin = local_dt1.astimezone(pytz.utc)
                mob_checkin = cin.strftime(new_format)
            if mob_checkout:
                upd_checkout_time = datetime.strptime(mob_checkout, "%Y-%m-%dT%H:%M")
                local_dt2 = local_dt.localize(upd_checkout_time, is_dst=None)
                cout = local_dt2.astimezone(pytz.utc)
                mob_checkout = cout.strftime(new_format)
            print(mob_checkin)
            print(mob_checkout)
            if user.id:
                vals = {
                    # 'employee_id': user.id,
                    'check_in': mob_checkin,
                    'check_out': mob_checkout
                }
                new_record = request.env['hr.attendance'].sudo().create(vals)
                args = {
                    'success': True, 'message': 'Success', 'id': new_record.id
                }
        return args

    @http.route('/attendance-adjustment', type='http', auth='public', website=True)
    def open_attendance_adjustment_form(self, **kw):
        return request.render("sg_attendance_adjustment_portal.attendance_adjustment_form")

    @http.route('/create/attendance-adjustment', type='http', auth='public', website=True)
    def create_attendance_adjustment(self, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        new_format = "%Y-%m-%d %H:%M:%S"
        create_check_in = kw.get('emp_check_in')
        create_check_out = kw.get('emp_check_out')
        print(create_check_in)
        print(create_check_out)
        check_in = datetime.strptime(create_check_in, "%Y-%m-%dT%H:%M")
        check_out = datetime.strptime(create_check_out, "%Y-%m-%dT%H:%M")
        att_date = check_in.date()
        print(att_date,';;;;;;;;;;;;;;;;;;;;;;;;;;')
        print(check_in)
        print(check_out)
        local_tz = request.env.user.tz
        local_dt = pytz.timezone(local_tz)
        local_dt1 = local_dt.localize(check_in, is_dst=None)
        local_dt2 = local_dt.localize(check_out, is_dst=None)
        cin = local_dt1.astimezone(pytz.utc)
        c_in = cin.strftime(new_format)
        cout = local_dt2.astimezone(pytz.utc)
        c_out = cout.strftime(new_format)
        note = kw.get('notes')

        values = {
            'name':emp.id,
            'att_date':att_date,
            'emp_check_in': c_in,
            'emp_check_out': c_out,
            'notes': kw.get('notes'),
        }
        # tmp_request = request.env['attendance.adjustment'].sudo().new(values)
        # values = tmp_request._convert_to_write(tmp_request._cache)
        request.env['attendance.adjustment'].sudo().create(values)

        # sql = "INSERT INTO attendance_adjustment(employee_id,name,att_date,emp_check_in,emp_check_out,notes)VALUES(%s,%s,%s,%s,%s)"
        # request.env.cr.execute(sql, (emp.id,emp.id ,att_date,c_in,c_out,note))
        # request.env.cr.commit()
        # myrequest.action_ask_approval()
        print('nvjnnnnnnn')
        # request.env['attendance.adjustment'].sudo().create(values)
        return request.render("sg_attendance_adjustment_portal.attendance_adjustment_web_form_message")

