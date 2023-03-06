from collections import OrderedDict
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from datetime import datetime, time, timedelta

import logging

_logger = logging.getLogger(__name__)


class SkipReqPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(SkipReqPortal, self)._prepare_portal_layout_values()
        skip_request_count = request.env['hr.skip.installment'].search_count([])
        values.update({
            "skip_request_count": skip_request_count,
        })
        return values

    def get_domain_my_skips(self, user):
        emp = request.env['hr.employee'].search([('employee_id.user_id', '=', user.id)],
                                                limit=1)
        return [
            ('employee_id', '=', emp and emp.id or False),
        ]

    @http.route(['/skip/requests/form', '/skip/requests/form/page/<int:page>'], type='http', website=True, auth='user')
    def skip_request(self, page=1, sortby=None, filterby=None, **kw):
        user = request.env.user
        values = self._prepare_portal_layout_values()
        skip_request = request.env['hr.skip.installment']
        skips = request.env['hr.skip.installment'].sudo().search([('employee_id.user_id', '=', user.id)])
        domain = [('employee_id.user_id', '=', user.id)]

        emp = request.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)

        installment_domain = [('employee_id.user_id', '=', [user.id]),('state', 'in', ['paid'])]
        skip_installment_ids = request.env['hr.advance.salary'].search(installment_domain)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'draft': {'label': _('Draft'), 'domain': [('state', '=', 'draft')]},
            'confirm': {'label': _('Confirm'), 'domain': [('state', '=', 'confirm')]},
            'open': {'label': _('Waiting Approval'), 'domain': [('state', '=', 'open')]},
            'refuse': {'label': _('Refused'), 'domain': [('state', '=', 'refuse')]},
            'approve': {'label': _('Approved'), 'domain': [('state', '=', 'approve')]},
            'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
        }

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        skip_request_count = skip_request.search_count(domain)

        pager = request.website.pager(
            url='/skip/requests/form',
            url_args={'sortby': sortby, 'filterby': filterby},
            total=skip_request_count,
            page=page,
            step=10
        )

        skip = skip_request.sudo().search(
            domain,
            order=order,
            limit=10,
            offset=pager['offset']
        )
        values.update({
            'skip_installment': skip_installment_ids.with_context({'employee_id': emp and emp.id or False}).name_get(),
            'skips': skip,
            'pager': pager,
            'page_name': 'Skips',
            'default_url': '/skip/requests/form',
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'sortby': sortby,
            'filterby': filterby,
        })

        return request.render("sg_skip_installment_portal.skip_form", values)

    @http.route(['/skip/requests/form/<int:skips_id>'], type='http', auth="user", website=True)
    def skip_request_portal_detail(self, skips_id, access_token=None, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        skip_sudo = self._document_check_access('hr.skip.installment', skips_id, access_token=access_token)
        installment_domain = [('state', 'in', ['paid'])]
        skip_installment_ids = request.env['hr.advance.salary'].search(installment_domain)
        print('Employee ID',emp)
        print('User ID',user)


        print(skip_installment_ids)
        values = {
            'skip_installment': skip_installment_ids.with_context({'employee_id': emp and emp.id or False}).name_get(),
            'skip_rec': skip_sudo,
            'token': access_token,
        }
        print(skip_sudo.id)

        values['pms'] = http.request.env['hr.employee'].search([('id', '=', skip_sudo.employee_id.id)])
        print(values)
        return request.render("sg_skip_installment_portal.portal_skip_form", values)

    @http.route('/skip-request', type='http', auth='public', website=True)
    def open_skip_form(self, **kw):
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        installment_domain = [('employee_id.user_id', '=', [user.id]),('state', '=', 'approve2')]
        skip_installment_ids = request.env['hr.advance.salary'].search(installment_domain)
        print('skip', skip_installment_ids.name)
        return request.render("sg_skip_installment_portal.skip_installment_form", {
            "skip_installment": skip_installment_ids
        })

    @http.route('/create/skip-request', type='http', auth='public', website=True)
    def create_skip_request(self, **kw):
        # new_format = "%Y-%m-%d %H:%M:%"
        # payment_start = kw.get('date')
        # time_start = datetime.strptime(payment_start, "%Y-%m-%dT%H:%M")
        # payment_start = time_start.strftime(new_format)
        user = request.env.user
        emp = request.env['hr.employee'].search([('user_id', '=', user.id)],
                                                limit=1)
        values = {
            # 'date': payment_start,
            'employee_id':emp.id,
            'date': kw.get('date'),
            'advance_salary_id': kw.get('advance_salary_id'),
            'name': kw.get('name'),
        }
        request.env['hr.skip.installment'].sudo().create(values)

        return request.render("sg_skip_installment_portal.skip_request_web_form_message", {})
