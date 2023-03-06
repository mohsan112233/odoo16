from datetime import timedelta, datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime


class AttendanceAdjustment(models.Model):
    _name = 'attendance.adjustment'
    _description = 'Attendance Adjustment Request'
    _inherit = ['hr.attendance', 'mail.thread', 'mail.activity.mixin']



    def default_employee(self):
        return self.env.context.get('default_employee_id') or self.env.user.employee_id


    #name = fields.Many2one('res.users', 'Employee Name', default=lambda self: self.env.user)
    name = fields.Many2one('hr.employee', string='Employee Name',default=default_employee)
    emp_check_in = fields.Datetime(string="Actual Check In")
    emp_check_out = fields.Datetime(string="Actual Check Out")

    state = fields.Selection(
        [('draft', 'Draft'), ('to_be_approved', 'Request'), ('approve', 'Approved'),
         ('refuse', 'Refused'),('done','Done')], readonly=True, default='draft', copy=False, string="Status")
    notes = fields.Text(string='Reason')
    responsible_id = fields.Many2one('res.users', string="Approver", related='name.parent_id.user_id')
    attendance_count = fields.Integer(string='Attendances', compute='get_attendance_count')


    def open_employee_request(self):
        return {
            'name': _('Attendance'),
            'domain': [('employee_id', '=', self.name.id)],
            'view_type': 'form',
            'res_model': 'hr.attendance',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def get_attendance_count(self):
        count = self.env['hr.attendance'].search_count([('employee_id', '=', self.name.id)])
        self.attendance_count = count

    def action_ask_approval(self):
        # if self.emp_check_in:
        #     time = datetime.strptime(str(self.emp_check_in),"%Y-%m-%d %H:%M:%S")
        #     new_time = time - timedelta(hours=5)
        #     self.emp_check_in = new_time
        self.write({'state': 'to_be_approved'})
        self.activity_update()

    def action_confirm(self):
        self.write({'state': 'approve'})
        self.activity_update()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Request Approved',
                'type': 'rainbow_man',
            }
        }

    def action_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    def _get_responsible_for_approval(self):
        if self.state == 'to_be_approved' and self.responsible_id:
            return self.responsible_id
        return self.env['res.users']

    def activity_update(self):
        to_clean, to_do = self.env['attendance.adjustment'], self.env['attendance.adjustment']
        for plan in self:
            if plan.state == 'draft':
                to_clean |= plan
            elif plan.state == 'to_be_approved':
                plan.activity_schedule(
                    'sg_attendance_adjustment_request.mail_act_schedule_attendance_adjustment',
                    user_id=plan.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif plan.state == 'approve':
                to_clean |= plan

        if to_clean:
            to_clean.activity_unlink(['sg_attendance_adjustment_request.mail_act_schedule_attendance_adjustment'])

    def create_attendance(self):
        search_attendance = self.env['hr.attendance']
        print("here boi")
        adjusted_check_in = datetime.strftime(self.emp_check_in, '%Y-%m-%d')
        print('My',adjusted_check_in)
        search_record = search_attendance.search(
            [('employee_id', '=', self.name.id),('attend_check_in','=',adjusted_check_in)])
        print('My search record', search_record)
        if not self.check_out:
            print('My create')
            search_record.write({
                'check_in': self.emp_check_in,
                'check_out': self.emp_check_out,

            })
        else:
            print('My write')
            search_record.write({
                'check_in': self.emp_check_in,
                'check_out': self.emp_check_out,

            })
        return self.write({'state': 'done'})




