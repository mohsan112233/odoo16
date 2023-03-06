from odoo import models, fields, api

from odoo.exceptions import UserError, ValidationError, MissingError


class AnnualLeaves(models.Model):
    _inherit = 'hr.leave.allocation'

    def action_validate(self):
        print("employee", self.holiday_status_id)
        for t in self:
            if t.holiday_status_id.name == 'Annual Leave':
                for rac in t.employee_ids:
                    print(rac.name)
                    permanent = self.env["hr.contract.history"].search(
                        [('employee_id', '=', rac.id)
                         ])
                    state = 0
                    for i in permanent.contract_ids:
                        if i.state == 'open' and i.date_end == False:
                            state = 1
                        print(i.date_end)
                        print(i.state)

                    if state == 0:
                        raise ValidationError(
                            f"{rac.name} is not permanent only permanent employee can apply for Annual leave")

                super(AnnualLeaves, self).action_validate()
                self.count_leaves_leaves_action()
            else:

                super(AnnualLeaves, self).action_validate()
                self.count_leaves_leaves_action()
