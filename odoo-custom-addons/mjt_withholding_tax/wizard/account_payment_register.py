# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    wht_tax_line_ids = fields.One2many("withholding.tax.line", 'payment_reg_id', string="Payment Register Line")
    withholding_tax_id = fields.Many2one('account.tax', string="Withholding Tax",
                                         domain=[("withholding_tax", "=", True)])
    amount_withholding = fields.Float(string="Amount WHT")

    @api.onchange('withholding_tax_id', 'amount')
    def _onchange_wth_tax_amount(self):
        if self.withholding_tax_id:
            if self.amount != 0:
                self.amount_withholding = self.amount * self.withholding_tax_id.amount / 100
            else:
                self.amount_withholding = 0
        else:
            self.amount_withholding = 0

    @api.model
    def _get_wizard_values_from_batch(self, batch_result):
        print("_get_wizard_values_from_batch OVERRIDE RUNNING..................")
        res = super(AccountPaymentRegister, self)._get_wizard_values_from_batch(batch_result)

        temp = []
        if batch_result:
            move_id = False
            for data in batch_result['lines'][:1]:
                move_line_id = self.env['account.move.line'].browse(data.id)
                move_id = move_line_id.move_id
            if move_id:
                # payment_id = self.env['account.payment'].search([('ref','=',move_id.name)])
                # if payment_id and not payment_id.is_wht_trx:
                # group invoice line by withholding_tax
                wht_tax_ids = []
                for rec in move_id.invoice_line_ids:
                    if rec.withholding_tax_id and rec.withholding_tax_id.id not in wht_tax_ids:
                        wht_tax_ids.append(rec.withholding_tax_id.id)
                # sum witholding_subtotal by tax
                for tax in wht_tax_ids:
                    subtotal_amount = 0
                    for move in move_id.invoice_line_ids:
                        if move.withholding_tax_id and move.withholding_tax_id.id == tax:
                            subtotal_amount += move.withholding_subtotal

                    tax_id = self.env['account.tax'].browse(tax)
                    vals = {
                        "tax_id": tax,
                        "name": tax_id.name,
                        "amount_withholding": subtotal_amount,
                    }
                    temp.append((0, 0, vals))

                if not move_id.wht_executed:
                    self.write({"wht_tax_line_ids": False})
                    self.write({"wht_tax_line_ids": temp})

        return res

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id',
                 'payment_date')
    def _compute_amount(self):
        # print("----_compute_amount OVERRIDE RUNNING")
        for wizard in self:
            wht_amount = 0
            if wizard.wht_tax_line_ids:
                wht_amount = sum(rec.amount_withholding for rec in wizard.wht_tax_line_ids)

            if wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                wizard.amount = wizard.source_amount_currency - wht_amount
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                wizard.amount = wizard.source_amount - wht_amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount,
                                                                                 wizard.currency_id, wizard.company_id,
                                                                                 wizard.payment_date)
                wizard.amount = amount_payment_currency - wht_amount

    @api.depends('amount')
    def _compute_payment_difference(self):
        # print("_compute_payment_difference OVERRIDE RUNNING.....................")
        for wizard in self:
            wht_amount = 0
            if wizard.wht_tax_line_ids:
                wht_amount = sum(rec.amount_withholding for rec in wizard.wht_tax_line_ids)
            if wizard.source_currency_id == wizard.currency_id:
                # Same currency.
                wizard.payment_difference = wizard.source_amount_currency - wizard.amount - wht_amount
            elif wizard.currency_id == wizard.company_id.currency_id:
                # Payment expressed on the company's currency.
                wizard.payment_difference = wizard.source_amount - wizard.amount - wht_amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = wizard.company_id.currency_id._convert(wizard.source_amount,
                                                                                 wizard.currency_id, wizard.company_id,
                                                                                 wizard.payment_date)
                wizard.payment_difference = amount_payment_currency - wizard.amount - wht_amount

    # def _create_payments(self):
    #     print("_create_payments OVERRIDE RUNNING........................")
    #     res = super(AccountPaymentRegister, self)._create_payments()
    #     print('sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssseeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
    #     if self.withholding_tax_id:
    #         print('tax id', self.withholding_tax_id.name)
    #         if self.amount_withholding:
    #             print(self.amount_withholding)
    #             inv_id = self.env['account.payment'].search(
    #                 [('partner_id', '=', self.partner_id.id), ('payment_type', '=', 'outbound'),
    #                  ('ref', '=', self.communication), ('date', '=', self.payment_date)], limit=1)
    #             if inv_id:
    #                 print('inv_id', inv_id)
    #                 inv_id.write({
    #                     'withholding_tax_id': self.withholding_tax_id,
    #                     'amount_withholding': self.amount_withholding,
    #                 })
    #
    #
    #
    #     return res
    def prepare_journal_line(self):

        return {
            'name': 'Discount',
            'quantity': 1,
            'debit': self.amount_withholding,
            'account_id': self.withholding_tax_id.invoice_repartition_line_ids.account_id.id,
            'sequence': 500000,
        }


class WithholdingTaxLine(models.TransientModel):
    _name = 'withholding.tax.line'

    payment_reg_id = fields.Many2one('account.payment.register', string="Account Payment Register")
    tax_id = fields.Many2one('account.tax', string="Taxes")
    name = fields.Char(string="Description")
    amount_withholding = fields.Float(string="Amount WHT")
