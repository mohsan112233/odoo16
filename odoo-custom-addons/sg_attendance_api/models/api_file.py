from odoo import models, fields, api
from datetime import datetime, time, timedelta


class ApiAttendance(models.Model):
    _inherit = 'hr.attendance'

    my_new_checkin = fields.Date('Date-Checkin', compute="_get_current_checkin", store=True, default=False)

    @api.depends('check_in')
    def _get_current_checkin(self):
        for rec in self:
            date = datetime.strftime(rec.check_in, '%Y-%m-%d %H:%M:%S')
            new_checkin = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').date()
            print(new_checkin)
            rec.my_new_checkin = new_checkin
