from odoo import models, fields, api


class SaleViewInherit(models.Model):
    _inherit = 'purchase.order'

    def check_reg_customer(self):
        if self.partner_id.x_studio_many2one_field_RZnWk:
            if 'Unregistered' in self.partner_id.x_studio_many2one_field_RZnWk.name:
                return self.get_unregistered_report_values()
            else:
                return self.get_registered_report_values()
        else:
            return self.get_registered_report_values()

    remarks_field = fields.Char(string="Remarks")
