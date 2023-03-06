# -*- coding: utf-8 -*-
from odoo import models, fields, api


class salary(models.Model):
    _name = "loan.type"
    name = fields.Char(string = "Name")
    code = fields.Char(string = "Code")

class Loan(models.Model):
    _inherit = "hr.advance.salary"
    loan_type = fields.Many2one('loan.type',string = "Loan Type")


