from odoo import fields, models, api
from datetime import datetime


class AccountPayment(models.Model):
    _name = 'draft.attendance'

    user_id = fields.Integer(string="User ID")
    att_date = fields.Date(string="Att Date")
    att_time = fields.Datetime(string="Att Time")
    verify_mode = fields.Integer(string="Verify Mode")
    att_mode = fields.Integer(string="Att Mode")
    device_id = fields.Integer(string="Device ID")
    device_name = fields.Char(string="Device Name")
