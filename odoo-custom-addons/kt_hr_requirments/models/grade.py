# -*- coding: utf-8 -*-
from odoo import models, fields, api


class salary(models.Model):

    _name = "employee.grade"
    _rec_name='g_name'

    g_name = fields.Char(string = "Name")
    g_code = fields.Char(string = "Code")

