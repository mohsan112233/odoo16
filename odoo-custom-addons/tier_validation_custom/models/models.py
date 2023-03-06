# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class purchase(models.Model):
    _inherit = 'purchase.order'
    v_users = fields.Many2one('tier.validation.custom')

    def activity_update(self):
        to_clean, to_do = self.env['tier.validation.custom'], self.env['tier.validation.custom']
        for plan in self:
            if plan.state == 'draft':
                to_clean |= plan
            elif plan.state == 'to_be_approved':
                plan.activity_schedule(
                    'tier_validation_custom.mail_act_approval_request',
                    user_id=plan.sudo()._get_responsible_for_approval().id or self.env.user.id)
            elif plan.state == 'approve':
                to_clean |= plan

        if to_clean:
            to_clean.activity_unlink(['tier_validation_custom.mail_act_approval_request'])

    def button_confirm(self):
        check = 0
        check2 = 1
        context = self._context

        current_uid = context.get('uid')

        user = self.env['res.users'].sudo().browse(current_uid)
        print(user.id)
        a = '''<span style='font-size:12.0pt;mso-bidi-font-size: 11.0pt;line-height:107%;font-family:"Times New Roman",serif;mso-fareast-font-family: Calibri;mso-fareast-theme-font:minor-latin;mso-ansi-language:EN-US;mso-fareast-language: EN-US;mso-bidi-language:AR-SA'>Operate <span style='font-size:12.0pt; mso-bidi-font-size:11.0pt;line-height:107%;font-family:"Times New Roman",serif; mso-fareast-font-family:Calibri;mso-fareast-theme-font:minor-latin;mso-ansi-language: EN-US;mso-fareast-language:EN-US;mso-bidi-language:AR-SA;mso-bidi-font-weight: bold'> the sonographic equipment and manipulate the parameters to achieve diagnostic images of optimum quality'''
        li = []
        # print(len(a))
        # a = a[100:]
        # print(a[100:])
        for i in range(500):
            # print(i)
            if i == '>':
                # print(i)
                s = int(a.find('>'))
                li.append(i)
        for i in range(500):
            s = int(a.find('>'))
            e = int(a.find('<'))
            if s:
                m = a[:s]
                n = a[e:]
                # print(s, 's')
                # print(a)
        # print('saad', li)
        # print(a)

        res = super(purchase, self).button_confirm()

        module_ids = self.env['tier.validation.custom'].sudo().search([('model_cus.name', '=', 'Purchase Order')])
        # print('dssssss', module_ids)
        if module_ids:
            # print(module_ids)
            li = [('id', '=', self.id)]
            for i in module_ids:
                v_users = i.validate_users
                n_v_users = i.non_validate_users
                print(n_v_users)
                li = [('id', '=', self.id)]
                fil = str(i.field_cus.name)
                op = str(i.operator)
                if v_users:
                    for k in v_users:
                        if k.id == user.id:
                            check = 1

                if n_v_users:
                    for n_v in n_v_users:
                        if n_v == user.id:
                            check2 = 0
                else:
                    check2 = 0

                try:
                    co = float(i.condition)
                except:
                    co = i.condition
                li.append((fil, op, co))
                purchase_ids = self.env['purchase.order'].sudo().search(li)

                # print(purchase_ids)

                if purchase_ids:
                    if check == 0 and check2 == 0:
                        print('Validation')
                        note = str(i.note)
                        self.activity_update()
                        raise ValidationError(f'{note}')
                    else:
                        print('Not validated', check, '.....', check2)
                else:
                    print('not purchase_ids', check, '.....', check2)

        return res


class ResConfigSettings(models.Model):
    _name = 'tier.validation.custom'
    _description = 'tier.validation.custom'
    model_cus = fields.Many2one('ir.model', string="Model")
    note = fields.Text('Note')
    field_cus = fields.Many2one('ir.model.fields', string="Field", domain="[('model_id', '=', model_cus)]")
    condition = fields.Char(string="Condition")
    validate_users = fields.Many2many('res.users', 'res_users_tier_validation_custom_rel', string="Allowed Users")
    non_validate_users = fields.Many2many('res.users', 'res_users_tier_validation_custom_rel_3',
                                          string="Restricted Users")
    operator = fields.Selection(
        selection=[
            (">", ">"),
            ("<", "<"),
            ("=", "="),
            ("!=", "!="),

        ],
        string="operator"
    )
