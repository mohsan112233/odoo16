# -*- coding: utf-8 -*-
from odoo import models, fields, api,_

class ContractHistory(models.Model):
    _inherit = 'hr.contract.history'

    @api.depends('employee_id.name')
    def _compute_display_name(self):
        for history in self:
            history.display_name = _("%s's Agreement History", history.employee_id.name)


class salary(models.Model):

    _inherit = 'hr.contract'

    wage = fields.Monetary(string='Monthly Salary')



class BloodGroup(models.Model):

    _inherit = 'hr.employee'
    contracts_count = fields.Integer(compute='_compute_contracts_count', string='Agreements Count')
    depend_ids = fields.One2many('hr.employee.line', 'depend_id')
    blood_group = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-')
    ],default='A+')
    grade = fields.Many2one('employee.grade', string='Employee Grade')

    @api.model
    def create(self, vals_list):
        print('mbdjsbjdbsjb')
        id = super(BloodGroup, self).create(vals_list)
        print(id.company_id.id)
        if not id.barcode:
            if id.company_id.id == 1:
                print(1)
                id.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence1')
            if id.company_id.id == 2:
                print(2)
                id.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence2')
            if id.company_id.id == 3:
                print(3)
                id.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence3')
            if id.company_id.id == 4:
                print(4)
                id.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence4')
            if id.company_id.id == 5:
                print(5)
                id.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence5')
        return id
    def generate_random_barcode(self):
        print('work')
        print(self.barcode)
        print(self.name)
        print(self.company_id.id)
        for i in self:
            if not i.barcode:
                if i.company_id.id == 1:
                    print(1)
                    i.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence1')
                if i.company_id.id == 2:
                    print(2)
                    i.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence2')
                if i.company_id.id == 3:
                    print(3)
                    i.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence3')
                if i.company_id.id == 4:
                    print(4)
                    i.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence4')
                if i.company_id.id == 5:
                    print(5)
                    i.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence5')


        # if self.company_id.id == 2:
        #     self.barcode = self.env['ir.sequence'].next_by_code('hr.employee.sequence_1') or 'New'
class DependsCount(models.Model):
    _name = 'hr.employee.line'
    depend_id = fields.Many2one('hr.employee')
    name = fields.Char('Name')
    relation = fields.Char('Relation')
