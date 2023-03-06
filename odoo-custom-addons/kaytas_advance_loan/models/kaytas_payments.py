from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime, time, timedelta, date
from odoo.exceptions import UserError, ValidationError, MissingError


class kaytasPayments(models.Model):
    _inherit = 'hr.advance.salary'
    to_date = fields.Date("To Date", default=lambda self: fields.Date.to_string(
        (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), required=True)
    full_pay = fields.Boolean(string='Fully Pay', default=False)
    max_loan = fields.Float(string='Max Loan/Advance can apply', compute='_max_loan_count', store=True)
    loan_group = fields.Boolean(String="Loan Group", compute='compute_loan_group')

    def compute_loan_group(self):
        for rec in self:
            group = self.env.user.has_group('ghani_attendance.max_loan_hide')
            if group:
                rec.loan_group = True
            else:
                rec.loan_group = False

    @api.onchange('payment', 'employee_id')
    def onchange_max_loan(self):
        self._max_loan_count()
        if self.employee_id and self.payment:
            for rac in self:
                print('lll')
                if rac.payment == 'fully':
                    wage = self.env["hr.contract"].search(
                        [('employee_id', '=', rac.employee_id.id)
                         ], limit=1, order='id desc')
                    print(wage)
                    # rac.max_loan = wage.wage / 2
                    rac.sudo().write({'max_loan': wage.wage / 2})
                else:
                    wage = self.env["hr.contract"].search(
                        [('employee_id', '=', rac.employee_id.id)
                         ], limit=1, order='id desc')
                    print(wage)
                    # rac.max_loan = (62.5 / 100) * wage.wage
                    rac.sudo().write({'max_loan': (62.5 / 100) * wage.wage})

    def _max_loan_count(self):
        for rac in self:
            print('lll')
            if rac.payment == 'fully':
                print('hi')
                date = rac.request_date
                request_day = date.strftime('%d')
                if rac.request_date and rac.employee_id and int(request_day) > 15:
                    if rac.request_date and rac.employee_id:
                        permanent = self.env["hr.contract.history"].search(
                            [('employee_id', '=', rac.employee_id.id)
                             ])
                        state = 0
                        for i in permanent.contract_ids:
                            if i.state == 'open':
                                state = 1
                            print(i.date_end)
                            print(i.state)
                        if state == 0:
                            pass
                            # raise ValidationError(
                            #     f"{rac.employee_id.name} is not permanent only permanent employee can apply for loan")
                    print('44')
                    wage = self.env["hr.contract"].search(
                        [('employee_id', '=', rac.employee_id.id)
                         ], limit=1, order='id desc')
                    print(wage)
                    # rac.max_loan = wage.wage / 2
                    rac.sudo().write({'max_loan': wage.wage / 2})


                elif rac.request_date and rac.employee_id and int(request_day) < 15:
                    print('lll', request_day)
                    # raise ValidationError(
                    #     f"At this {rac.request_date.date()} date  {rac.employee_id.name} is not eligible for advance")
                else:
                    pass

            else:
                print('lllllllllllllllllllllll')

                if rac.request_date and rac.employee_id:
                    permanent = self.env["hr.contract.history"].search(
                        [('employee_id', '=', rac.employee_id.id)
                         ])

                    state = 0
                    for i in permanent.contract_ids:
                        if i.state == 'open':
                            state = 1
                    if state == 0:
                        pass
                        # raise ValidationError(
                        #     f"{rac.employee_id.name} is not permanent only permanent employee can apply for loan")

                    loan_date = self.env["hr.advance.salary"].search(
                        [('employee_id', '=', rac.employee_id.id), ('payment', '=', 'partially'), ('state', '=', 'paid')
                         ], limit=1, order='id desc')
                    print(loan_date, 'mmmm')
                    if loan_date:
                        print('1152')
                        loan_payslips = loan_date.payslip_line_ids
                        deduct_amount = 0
                        for loan_payslip in loan_payslips:
                            deduct_amount = deduct_amount + loan_payslip.amount
                        if loan_date.amount_to_pay <= loan_date.amount_paid:
                            deduct_amount = 'Pass'
                            wage = self.env["hr.contract"].search(
                                [('employee_id', '=', rac.employee_id.id)
                                 ], limit=1, order='id desc')
                            print(wage, 'ooo')

                            # rac.max_loan = (62.5 / 100) * wage.wage
                            rac.sudo().write({'max_loan': (62.5 / 100) * wage.wage})

                        if loan_date and deduct_amount != 'Pass':
                            print(loan_date, 'pass')
                            date_half = rac.request_date - loan_date.request_date
                            print(date_half)
                            date_half = date_half.total_seconds() / 3600.0
                            date_half = date_half / 24
                            print(date_half, 'llllpp')
                            if rac.request_date and rac.employee_id and date_half > 365:
                                print('lllll', date_half)
                                wage = self.env["hr.contract"].search(
                                    [('employee_id', '=', rac.employee_id.id)
                                     ], limit=1, order='id desc')
                                print(wage)
                                # rac.max_loan = wage.wage * 3
                                # rac.max_loan = (62.5 / 100) * wage.wage
                                rac.sudo().write({'max_loan': (62.5 / 100) * wage.wage})

                            elif rac.request_date and rac.employee_id and date_half < 365:
                                print('ooo')
                                # raise ValidationError(
                                #     f"At this {rac.request_date.date()} date   {rac.employee_id.name} is not eligible for loan")
                            else:
                                pass
                    else:
                        wage = self.env["hr.contract"].search(
                            [('employee_id', '=', rac.employee_id.id)
                             ], limit=1, order='id desc')
                        print(wage)
                        rac.sudo().write({'max_loan': (62.5 / 100) * wage.wage})

                        # rac.max_loan = (62.5 / 100) * wage.wage

    def calculate_button_action(self):
        # self._max_loan_count()
        if self.request_amount > self.max_loan:
            pass
            # raise ValidationError(
            #     f"{self.employee_id.name} can get maximum {self.max_loan} loan")
        super(kaytasPayments, self).calculate_button_action()

    def action_confirm(self):
        # self._max_loan_count()
        if self.request_amount > self.max_loan:
            pass
            # raise ValidationError(
            #     f"{self.employee_id.name} can get maximum {self.max_loan} loan")
        super(kaytasPayments, self).action_confirm()

    # def action_paid(self):
    #     self.full_pay = True
    #     super(kaytasPayments, self).action_paid()
    def set_draft(self):
        self.full_pay = False
        self.state = 'draft'

    def onchange_full_pay(self):
        # self.deduction_amount = self.amount_to_pay
        # self.payment_end_date = self.to_date
        # self.env.cr.commit()
        # print('kkk...')
        if self.amount_to_pay > 0:
            self.sudo().write(
                {'deduction_amount': self.amount_to_pay, 'payment_end_date': self.to_date}
            )
