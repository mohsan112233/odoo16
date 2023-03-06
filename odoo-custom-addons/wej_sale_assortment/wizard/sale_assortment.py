import logging
from odoo import models, fields, api
import random
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')

try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')

try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class SaleAssortment(models.TransientModel):
    _name = 'sale.assortment'
    _description = "Sale Assortment"

    product_id = fields.Many2one('product.template', string="Product",required=1)
    total_qty = fields.Float('Total Quantity')
    assortment_ids = fields.Many2many("product.attribute.value",related='product_id.assortment_ids', string="Assortment")
    temp_autocomplete_lines = fields.Many2many('assortment.template', store=False, compute='_compute_template_autocomplete_ids')
    template_id = fields.Many2one('assortment.template',domain="[('id','in',temp_autocomplete_lines)]" ,string='Select Assortment',store=True)
    color_ids = fields.Many2one('product.attribute.value', domain="[('id','in',assortment_ids)]",
                                      string='Color', store=True)
    @api.depends('product_id','color_ids')
    def _compute_template_autocomplete_ids(self):
        list_1 = []
        line_id = self.env['prod.assort.line'].search([('temp_id', '=', self.product_id.id),
                                                               ('color_ids', '=',self.color_ids.id
                                                                 )])
        for rec in line_id.size_ids:
            print(rec)


            list_1.append(rec.id)
        try:
            self.sudo().write({'temp_autocomplete_lines': [(6, 0, list_1)]})
        except:
            raise ValidationError(f"{list_1}")
    def assign_ratio(self):
        li = []
        # for op in self.color_ids:

        total = sum(v.ratio for v in self.template_id.line_ids)
        val = self.total_qty / total
        products_v = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id),
                                                         ('product_template_attribute_value_ids.product_attribute_value_id','=',self.color_ids.id)])
        active_id = self.env.context.get('active_id')
        # print(active_id)
        print(products_v)
        for i in products_v:
            # print('fffff',i)
            for n in i.product_template_attribute_value_ids:
                # if n.attribute_id.name == 'Size':
                    # print(n,'pjssj')
                    # for s in i.value_ids:
                    line_id = self.env['assortment.template.line'].search([('temp_id', '=', self.template_id.id),
                                                                           ('product_line_id','=',n.product_attribute_value_id.id)])
                    # print(line_id)
                    vals = line_id.ratio * val
                    if line_id:
                        li.append([0, 0, {
                            'product_id': i.id,
                            'product_uom_qty': round(vals)
                        }])
        # for rec in self.template_id.line_ids:
            #     li.append([0, 0, {
            #         'product_id': self.product_id.id,
            #         'product_uom_qty': rec.ratio * val
            #     }])
        sale_order = self.env['sale.order'].search([('id','=',active_id)])

        sale_order.write({'order_line': li})
            #
            #


class PurchaseAssortment(models.TransientModel):
    _name = 'purchase.assortment'
    _description = "Sale Assortment"
    product_id = fields.Many2one('product.template', string="Product", required=1)
    total_qty = fields.Float('Total Quantity')
    assortment_ids = fields.Many2many("product.attribute.value", related='product_id.assortment_ids',
                                      string="Assortment")
    temp_autocomplete_lines = fields.Many2many('assortment.template', store=False,
                                               compute='_compute_template_autocomplete_ids')
    template_id = fields.Many2one('assortment.template', domain="[('id','in',temp_autocomplete_lines)]",
                                  string='Select Assortment', store=True)
    color_ids = fields.Many2one('product.attribute.value', domain="[('id','in',assortment_ids)]",
                                string='Color', store=True)
    @api.depends('product_id')
    def _compute_template_autocomplete_ids(self):
        domain = []
        if self.product_id:
            domain = [('product_id', '=', self.product_id.id)]
            # domain = []

        self.temp_autocomplete_lines = self.env['assortment.template'].search(domain, limit=20)


    def purchase_assign_ratio(self):
        li = []
        # for op in self.color_ids:

        total = sum(v.ratio for v in self.template_id.line_ids)
        val = self.total_qty / total
        products_v = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id),
                                                         (
                                                         'product_template_attribute_value_ids.product_attribute_value_id',
                                                         '=', self.color_ids.id)])
        active_id = self.env.context.get('active_id')
        # print(active_id)
        print(products_v)
        for i in products_v:
            # print('fffff',i)
            for n in i.product_template_attribute_value_ids:
                # if n.attribute_id.name == 'Size':
                # print(n,'pjssj')
                # for s in i.value_ids:
                line_id = self.env['assortment.template.line'].search([('temp_id', '=', self.template_id.id),
                                                                       ('product_line_id', '=',
                                                                        n.product_attribute_value_id.id)])
                # print(line_id)
                vals = line_id.ratio * val
                if line_id:
                    li.append([0, 0, {
                        'product_id': i.id,
                        'product_uom_qty': round(vals)
                    }])
        # for rec in self.template_id.line_ids:
        #     li.append([0, 0, {
        #         'product_id': self.product_id.id,
        #         'product_uom_qty': rec.ratio * val
        #     }])
        # sale_order = self.env['sale.order'].search([('id', '=', active_id)])
        #
        # sale_order.write({'order_line': li})
        #
        #
        purchase_order = self.env['purchase.order'].search([('id', '=', active_id)])
        print('dd',li)
        purchase_order.write({'order_line': li})



class GRNAssortment(models.TransientModel):
    _name = 'grn.assortment'
    _description = "Sale Assortment"
    product_id = fields.Many2one('product.template', string="Product", required=1)
    total_qty = fields.Float('Total Quantity')
    assortment_ids = fields.Many2many("product.attribute.value", related='product_id.assortment_ids',
                                      string="Assortment")
    temp_autocomplete_lines = fields.Many2many('assortment.template', store=False,
                                               compute='_compute_template_autocomplete_ids')
    template_id = fields.Many2one('assortment.template', domain="[('id','in',temp_autocomplete_lines)]",
                                  string='Select Assortment', store=True)
    color_ids = fields.Many2one('product.attribute.value', domain="[('id','in',assortment_ids)]",
                                string='Color', store=True)
    @api.depends('product_id')
    def _compute_template_autocomplete_ids(self):
        domain = []
        if self.product_id:
            domain = [('product_id', '=', self.product_id.id)]
            # domain = []

        self.temp_autocomplete_lines = self.env['assortment.template'].search(domain, limit=20)


    def purchase_assign_ratio(self):

        li = []
        # for op in self.color_ids:

        total = sum(v.ratio for v in self.template_id.line_ids)
        val = self.total_qty / total
        products_v = self.env['product.product'].search([('product_tmpl_id', '=', self.product_id.id),
                                                         (
                                                         'product_template_attribute_value_ids.product_attribute_value_id',
                                                         '=', self.color_ids.id)])
        active_id = self.env.context.get('active_id')
        # print(active_id)
        print(products_v)
        for i in products_v:
            # print('fffff',i)
            for n in i.product_template_attribute_value_ids:
                # if n.attribute_id.name == 'Size':
                # print(n,'pjssj')
                # for s in i.value_ids:
                line_id = self.env['assortment.template.line'].search([('temp_id', '=', self.template_id.id),
                                                                       ('product_line_id', '=',
                                                                        n.product_attribute_value_id.id)])
                # print(line_id)
                vals = line_id.ratio * val
                if line_id:
                    li.append([0, 0, {
                        'name': i.name,
                        'product_id': i.id,
                        'product_uom_qty': round(vals),
                        'location_id': grn_order.location_id.id,
                        'location_dest_id': grn_order.location_dest_id.id
                    }])
        # for rec in self.template_id.line_ids:
        #     li.append([0, 0, {
        #         'product_id': self.product_id.id,
        #         'product_uom_qty': rec.ratio * val

        grn_order = self.env['stock.picking'].search([('id', '=', active_id)])
        print('dd',li)
        grn_order.write({'move_ids_without_package': li})



class SaleAssortmentLine(models.TransientModel):
    _name="sale.assortment.line"

    sale_assortment = fields.Many2one('sale.assortment',string='Sale')
    product = fields.Many2one('product.product', string="Product")
    qty = fields.Float('Quantity')

