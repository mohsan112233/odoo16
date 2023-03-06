from collections import OrderedDict
from odoo import http, _
from odoo.http import request
import pytz
from datetime import date
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from datetime import datetime, time, timedelta
from odoo.exceptions import UserError, ValidationError, MissingError

import logging

_logger = logging.getLogger(__name__)


class AdvanceReqPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(AdvanceReqPortal, self)._prepare_portal_layout_values()
        advance_count = request.env['hr.advance.salary'].search_count([])
        values.update({
            "advance_count": advance_count,
        })
        return values

    def get_domain_my_advances(self, user):
        emp = request.env['hr.employee'].search([('employee_id.user_id', '=', user.id)],
                                                limit=1)
        return [
            ('employee_id', '=', emp and emp.id or False),
        ]

    # def _prepare_portal_layout_values(self):
    #     values = super(AdvanceReqPortal, self)._prepare_portal_layout_values()
    #     advance_count = request.env['hr.attendance'].search_count(self.get_domain_my_advances(request.env.user))
    #     values.update({
    #         'advance_count': advance_count,
    #     })
    #     return values

    # @http.route('/employee/request/form/', type='http', website=True, auth='public')
    # def employee_request(self, **kw):
    #     user_rec = request.env['hr.employee'].sudo().search([])
    #     return request.render("sg_advance_approval.create_request", {
    #             'user_rec': user_rec
    #     })

    # @http.route(['/employee/request/form/'], type="http", auth="public", website=True)
    # def patient_form(self, **kw):
    #     pro_rec = request.env['res.users'].sudo().search([])
    #
    #     return request.render("sg_advance_approval.create_request", {'pro_rec': pro_rec})
    #
    # @http.route('/create/advance/request/', type="http", auth="public", website=True)
    # def create_request(self, **kw):
    #     print("Data Received.........", kw)
    #     request.env['hr.advance.salary'].sudo().create(kw)
    #     return request.render("sg_advance_approval.employee_thanks", {})

    @http.route(['/advance/requests/form', '/advance/requests/form/page/<int:page>'],type='http', website=True, auth='user')
    def advance_request(self, page=1, sortby=None, filterby=None,**kw):
        user = request.env.user
        values = self._prepare_portal_layout_values()
        advance_salary = request.env['hr.advance.salary']
        advances = request.env['hr.advance.salary'].sudo().search([('employee_id.user_id', '=', user.id)])
        domain = [('employee_id.user_id','=',user.id)]

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'paid': {'label': _('Paid'), 'domain': [('state', '=', 'paid')]},
            'confirm': {'label': _('Confirm'), 'domain': [('state', '=', 'confirm')]},
            'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]},
            #'approve2': {'label': _('Second Approval'), 'domain': [('state', '=', 'approve2')]},
            'approve1': {'label': _('Approved'), 'domain': [('state', '=', 'approve1')]},
        }

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'request_amount': {'label': _('Amount'), 'order': 'request_amount desc'},

        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # filter
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        advance_count = advance_salary.search_count(domain)
        pager = request.website.pager(
            url = '/advance/requests/form',
            url_args={'sortby': sortby, 'filterby': filterby},
            total=advance_count,
            page=page,
            step=10
        )
        advance = advance_salary.sudo().search(domain, order=order, limit=10, offset=pager['offset'])
        values.update({
            'advances': advance,
            'pager': pager,
            'page_name': 'Advances',
            'default_url': '/advance/requests/form',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'sortby': sortby,
            'filterby': filterby,
        })
        return request.render("sg_advance_request_portal.advances_form", values)

        # adjustment view
    @http.route(['/advance/requests/form/<int:advance_id>'], type='http', auth="user", website=True)
    def advance_request_portal_detail(self, advance_id, access_token=None, **kw):
        user = request.env.user
        advance_sudo = self._document_check_access('hr.advance.salary', advance_id, access_token=access_token)
        values = {
            'advance_rec': advance_sudo,
            'token': access_token,
        }
        print(advance_sudo.id)

        values['pms'] = http.request.env['hr.employee'].search([('id', '=', advance_sudo.employee_id.id)])
        print(values)
        return request.render("sg_advance_request_portal.portal_advance_form", values)

    @http.route('/advance-request', type='http', auth='public', website=True)
    def open_advance_request_form(self, **kw):
        return request.render("sg_advance_request_portal.advance_request_form")

    @http.route('/create/advance-request', type='http', auth='public', website=True)
    def create_advance_request(self, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        user = request.env.user
        # advance = request.env["hr.advance.salary"].search([])
        # print(advance)
        # if kw.get('payment') == 'fully':
        #     print('hi')
        #     date_req = date.today()
        #     request_day = date_req.strftime('%d')
        #
        #     if int(request_day) > 15:
        #
        #         permanent = request.env["hr.contract.history"].search(
        #             [('employee_id.user_id', '=', user.id)
        #              ])
        #         state = 0
        #         for i in permanent.contract_ids:
        #             if i.state == 'open':
        #                 state = 1
        #
        #         if state == 0:
        #             raise ValidationError(
        #                 f"{user.name} is not permanent only permanent employee can apply for loan")
        #
        #         print('44')
        #         wage = request.env["hr.contract"].search(
        #             [('employee_id', '=', emp.id)
        #              ],limit=1, order='id desc')
        #         print(wage)
        #         max_loan = wage.wage / 2
        #
        #     elif int(request_day) < 15:
        #         print('lll', request_day)
        #         raise ValidationError(
        #             f"At this {date.today()} date the  {user.name} is not eligible for advance")
        #     else:
        #         pass
        #
        #     wage = request.env["hr.contract"].search(
        #         [('employee_id', '=', emp.id)
        #          ],limit=1, order='id desc')
        #     print(wage)
        #     max_loan = wage.wage / 2
        #     if max_loan < int(kw.get('request_amount')):
        #         raise ValidationError(
        #             f"{user.name}  Can get maximum {max_loan} Advance")
        # if kw.get('payment') == 'partially' :
        #     permanent = request.env["hr.contract.history"].search(
        #         [('employee_id', '=', emp.id)
        #          ])
        #     state = 0
        #     for i in permanent.contract_ids:
        #         if i.state == 'open':
        #             state = 1
        #     if state == 0:
        #         raise ValidationError(
        #             f"{user.name} is not permanent only permanent employee can apply for loan")
        #
        #     loan_date = request.env["hr.advance.salary"].search(
        #         [('employee_id', '=', emp.id), ('payment', '=', 'partially'),('state', '=', 'paid')
        #          ],limit=1, order='id desc')
        #     print(loan_date, 'mmmm')
        #     if loan_date:
        #
        #         print('1152')
        #         loan_payslips = loan_date.payslip_line_ids
        #         deduct_amount = 0
        #         for loan_payslip in loan_payslips:
        #             deduct_amount = deduct_amount + loan_payslip.amount
        #         if loan_date.amount_to_pay <= loan_date.amount_paid:
        #             deduct_amount = 'Pass'
        #             wage = self.env["hr.contract"].search(
        #                 [('employee_id.user_id', '=', user.id)
        #                  ],limit=1, order='id desc')
        #             print(wage, 'ooo')
        #             max_loan = wage.wage * 3
        #
        #         if loan_date and deduct_amount != 'Pass':
        #             print(loan_date, 'pass')
        #
        #             date_half = datetime.today() - loan_date.request_date
        #             print(date_half)
        #             date_half = date_half.total_seconds() / 3600.0
        #             date_half = date_half / 24
        #             print(date_half, 'llllpp')
        #             if date_half > 365:
        #
        #                 print('lllll', date_half)
        #                 wage = request.env["hr.contract"].search(
        #                     [('employee_id.user_id', '=', user.id)
        #                      ],limit=1, order='id desc')
        #                 print(wage)
        #                 max_loan = wage.wage * 3
        #
        #             elif date_half < 365:
        #                 print('ooo')
        #                 raise ValidationError(
        #                     f"At this {date.today()} date the  {user.name} is not eligible for loan")
        #             else:
        #                 pass
        #     else:
        #
        #
        #         wage = request.env["hr.contract"].search(
        #             [('employee_id.user_id', '=', user.id)
        #              ],limit=1, order='id desc')
        #         print(wage)
        #         max_loan = wage.wage * 3
        #         if max_loan < int(kw.get('request_amount')):
        #             raise ValidationError(
        #                 f"{user.name}  Can get maximum {max_loan} loan")
        # if kw.get('payment') == 'fully':
        #     if max_loan < int(kw.get('request_amount')):
        #         raise ValidationError(
        #             f"{user.name}  Can get maximum {max_loan} Advance")
        #
        # if kw.get('payment') == 'partially':
        #     if max_loan < int(kw.get('request_amount')):
        #         raise ValidationError(
        #             f"{user.name}  Can get maximum {max_loan} loan")
        #
        # print(']]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]')
        advance = request.env["hr.advance.salary"].search([])
        print(advance)
        new_format = "%Y-%m-%d %H:%M:%S"
        payment_start = kw.get('payment_start_date')
        time_start = datetime.strptime(payment_start, "%Y-%m-%dT%H:%M")
        payment_start = time_start.strftime(new_format)

        new_format = "%Y-%m-%d %H:%M:%S"
        payment_start = kw.get('payment_start_date')
        time_start = datetime.strptime(payment_start, "%Y-%m-%dT%H:%M")
        local_tz = request.env.user.tz
        local_dt = pytz.timezone(local_tz)
        local_dt1 = local_dt.localize(time_start, is_dst=None)
        new_time = local_dt1.astimezone(pytz.utc)
        new_time = new_time.strftime(new_format)
        user = request.env.user
        print('user',user)
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        values = {
            # 'max_loan':max_loan,
            'employee_id':emp.id,
            'payment_start_date': new_time,
            'request_amount': kw.get('request_amount'),
            'payment': kw.get('payment'),
            'reason': kw.get('reason'),
        }
        request.env['hr.advance.salary'].sudo().create(values)

        return request.render("sg_advance_request_portal.advance_request_web_form_message", {})