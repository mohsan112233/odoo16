
from odoo import api, fields, models, _

import odoo.addons.decimal_precision as dp

class PayslipLine(models.Model):
    _name = 'payslip.loan.line'
    _description = 'Payslip Line'

    advance_salary_id = fields.Many2one('hr.advance.salary')
    # payslip_id = fields.Many2one('hr.payslip', 'Payslip', required=True)
    # employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    date = fields.Datetime('Date', required=True)
    amount = fields.Float('Deduction Amount', digits=dp.get_precision('Account'), required=True)
    state = fields.Char(string='State',default='Draft',readoly='1')

    @api.onchange('date')
    def work_emp(self):
        print(';',self.advance_salary_id.name)
        emp = self.env['hr.advance.salary'].search([('name','=',self.advance_salary_id.name)])
        # print(emp)
        # self.employee_id =emp.id
        rs = 0
        for pay in emp.payslip_line_ids:
            rs = rs + pay.amount
        self.amount = emp.amount_to_pay
        print('advance_salary_id')


class PayslipLoan(models.Model):
    _inherit = 'hr.advance.salary'
    payslip_loan_ids = fields.One2many('payslip.loan.line', 'advance_salary_id')

    # @api.onchange('payslip_loan_ids')
    # def work_auto(self):
    #     print('jjj')
    #     self.payslip_loan_ids.employee_id = self.employee_id.id