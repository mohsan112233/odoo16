from odoo import models, fields, api


class SaleAssortment(models.Model):
    _inherit = 'product.template'
    assortment_ids = fields.Many2many('product.attribute.value',string="color",compute="_onchange_todo_command")

    @api.depends('attribute_line_ids')
    def _onchange_todo_command(self):
        for res in self:
            print('saad')
            list_1 = []
            for rec in res.attribute_line_ids:
                print(rec)
                if rec.attribute_id.name == 'Color':
                    for r in rec.value_ids:
                        list_1.append(r._origin.id)
                        print(list_1)
            try:

                res.assortment_ids = [(6, 0, list_1)]


            except:

                pass


class AssortmentTemplate(models.Model):
    _name = 'assortment.template'

    active = fields.Boolean('Active', default=True)
    name = fields.Char('Assortment Name')
    product_id = fields.Many2one('product.template', 'Product Template', store=True)
    line_ids = fields.One2many('assortment.template.line', 'temp_id')

    @api.onchange('product_id')
    def onchange_product_id(self):
        products_v = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id)])
        variants = []
        for rec in products_v:
            variants.append([0, 0, {
                'product_line_id': rec.id,
            }])
        self.sudo().write({'line_ids': variants})


class AssortmentLine(models.Model):
    _name = 'assortment.template.line'
    _rec_name = 'product_line_id'
    temp_id = fields.Many2one('assortment.template', store=True)
    product_line_ids = fields.Many2many('product.attribute.value', domain="[('attribute_id', '=', 'Size')]",
                                      string='Variant', store=True)
    product_line_id = fields.Many2one('product.attribute.value',domain="[('id','not in',product_line_ids),('attribute_id', '=', 'Size')]", string='Variant', store=True)
    ratio = fields.Float('Ratio', store=True)

    @api.onchange('product_line_id')
    def _onchange_todo_command(self):
        list_1 = []
        for rec in self.temp_id.line_ids:
            print(rec)
            if rec.product_line_id.id:
                list_1.append(rec.product_line_id.id)
        self.sudo().write({'product_line_ids': [(6, 0, list_1)]})
