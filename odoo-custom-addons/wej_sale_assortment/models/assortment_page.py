from odoo import models, fields, api
from odoo.exceptions import ValidationError
class AssortmentLine(models.Model):
    _name = 'prod.assort.line'
    variant_ids = fields.Many2many('product.attribute.value', string='variant', store=True, compute='_onchange_todo_command')
    # variant_ids = fields.Char(string='variant', store=True)
    temp_id = fields.Many2one('product.template', store=True)
    color_ids = fields.Many2one('product.attribute.value', domain="[('id','in',variant_ids),('attribute_id', '=', 'Color')]",
                                      string='Color', store=True)
    size_ids = fields.Many2many('assortment.template', string='Template', store=True)

    @api.depends('color_ids')
    def _onchange_todo_command(self):
        list_1 = []
        for rec in self.temp_id.attribute_line_ids:
            print(rec)
            if rec.attribute_id.name == 'Color':
                for r in rec.value_ids:

                    list_1.append(r._origin.id)
                    print(list_1)
        try:
            self.variant_ids = [(6, 0, list_1)]

            # self.temp_id.sudo().write({'assortment_ids': [(6, 0, list_1)]})
            # self.temp_id.a
        except:

            raise ValidationError(f"{list_1}")
class Assort(models.Model):
    _inherit = 'product.template'

    assort_ids = fields.One2many(
        comodel_name="prod.assort.line",
        inverse_name="temp_id",
        string="assortment",

    )

