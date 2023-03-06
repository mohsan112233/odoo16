# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Ijaz Ahammed (odoo@cybrosys.com)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
import babel
from datetime import date, datetime, time

from dateutil.relativedelta import relativedelta

from odoo import models, api, fields, tools, _
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date


class PayslipLateCheckIn(models.Model):
    _inherit = 'hr.payslip'

    late_check_in_ids = fields.Many2many('late.check_in')
    default_struct_id = fields.Many2one('hr.payroll.structure', compute='_compute_default_struct_id')

    def _compute_default_struct_id(self):
        for structure_type in self:
            sorted_structures = sorted(structure_type.struct_ids, key=lambda struct: struct.regular_pay, reverse=True)
            structure_type.default_struct_id = sorted_structures[0] if sorted_structures else False

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """
        function used for writing late check-in record in payslip
        input tree.

        """
        res = []
        late_check_in_type = self.env.ref('employee_late_check_in.late_check_in')
        contract = self.contract_id
        late_check_in_id = self.env['late.check_in'].search([('employee_id', '=', self.employee_id.id),
                                                             ('date', '<=', self.date_to),
                                                             ('date', '>=', self.date_from),
                                                             ('state', '=', 'approved'),
                                                             ])
        input_type = self.env['hr.payslip.input.type'].search([('name', '=', 'Late'),
                                                             ('code', '<=', 'LC'),
                                                             ])
        print(input_type)
        new_input = input_type.name
        print(new_input)
        amount = late_check_in_id.mapped('amount')
        print(amount)
        cash_amount = sum(amount)
        print(cash_amount)
        if late_check_in_id:
            self.late_check_in_ids = late_check_in_id
            input_data = {
                'input_type_id': input_type.id,
                'code': late_check_in_type.code,
                'amount': cash_amount,
                'contract_id': contract.id,
            }
            print(input_data)
            res.append(input_data)
        return res

    @api.model
    def get_contract(self, employee, date_from, date_to):
        """
        @param employee: recordset of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """
        # a contract is valid if it ends between the given dates
        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
        # OR if it starts between the given dates
        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
        # OR if it starts before the date_from and finish after the date_end (or never finish)
        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False), ('date_end', '>=', date_to)]
        clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open'), '|',
                        '|'] + clause_1 + clause_2 + clause_3
        return self.env['hr.contract'].search(clause_final).ids

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []

        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (
            employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.structure_type_id:
            return
        # self.struct_id = self.contract_id.default_struct_id
        if self.contract_id:
            contract_ids = self.contract_id.ids
        # computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self._get_worked_day_lines()
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines

        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        input_lines = self.input_line_ids.browse([])
        for r in input_line_ids:
            input_lines += input_lines.new(r)
        self.input_line_ids = input_lines
        return


def action_payslip_done(self):
    """
    function used for marking deducted Late check-in
    request.

    """
    for recd in self.late_check_in_ids:
        recd.state = 'deducted'
    return super(PayslipLateCheckIn, self).action_payslip_done()
