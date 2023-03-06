from odoo import models, fields, api


class SaleViewInherit(models.Model):
    _inherit = 'account.move'
    _description = 'Account Move Inherit Fields'

    def check_reg_customer(self):
        if 'Unregistered' in self.journal_id.name:
            return self.get_unregistered_report_values()
        else:
            return self.get_registered_report_values()

    remarks_field = fields.Char(string="Remarks")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ntn1 = fields.Char(string="NTN. No")
#     x_studio_many2one_field_RZnWk = fields.Boolean  (string="NTN. No")


class ResCompany(models.Model):
    _inherit = 'res.company'
    ntn1 = fields.Char(string="NTN No.")
