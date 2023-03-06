
from odoo import api, fields, models, _



class EmployeeAdvanceSalary(models.Model):
    _inherit = "hr.advance.salary"

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  )