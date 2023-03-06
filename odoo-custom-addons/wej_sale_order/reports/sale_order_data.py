from odoo import models, fields, api

from PIL import Image, ImageOps
# We can preload Ico too because it is considered safe
from PIL import IcoImagePlugin
try:
    from PIL.Image import Transpose, Palette, Resampling
except ImportError:
    Transpose = Palette = Resampling = Image

from random import randrange

from odoo.exceptions import UserError
from odoo.tools.translate import _


# Preload PIL with the minimal subset of image formats we need
Image.preinit()
Image._initialized = 2

# Maps only the 6 first bits of the base64 data, accurate enough
# for our purpose and faster than decoding the full blob first
FILETYPE_BASE64_MAGICWORD = {
    b'/': 'jpg',
    b'R': 'gif',
    b'i': 'png',
    b'P': 'svg+xml',
}

EXIF_TAG_ORIENTATION = 0x112
# The target is to have 1st row/col to be top/left
# Note: rotate is counterclockwise
EXIF_TAG_ORIENTATION_TO_TRANSPOSE_METHODS = { # Initial side on 1st row/col:
    0: [],                                              # reserved
    1: [],                                              # top/left
    2: [Transpose.FLIP_LEFT_RIGHT],                     # top/right
    3: [Transpose.ROTATE_180],                          # bottom/right
    4: [Transpose.FLIP_TOP_BOTTOM],                     # bottom/left
    5: [Transpose.FLIP_LEFT_RIGHT, Transpose.ROTATE_90],# left/top
    6: [Transpose.ROTATE_270],                          # right/top
    7: [Transpose.FLIP_TOP_BOTTOM, Transpose.ROTATE_90],# right/bottom
    8: [Transpose.ROTATE_90],                           # left/bottom
}

# Arbitrary limit to fit most resolutions, including Samsung Galaxy A22 photo,
# 8K with a ratio up to 16:10, and almost all variants of 4320p
IMAGE_MAX_RESOLUTION = 50e6


class InheritResPartner(models.Model):
    _inherit = 'res.partner'
    x_studio_many2one_field_RZnWk = fields.Many2one('account.journal')


class SaleReportWej(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale Order Report'

    remarks_field = fields.Char(string="Remarks")

    def image_data_uri(self,base64_source):
        """This returns data URL scheme according RFC 2397
        (https://tools.ietf.org/html/rfc2397) for all kind of supported images
        (PNG, GIF, JPG and SVG), defaulting on PNG type if not mimetype detected.
        """
        import base64

        aa = str(type(base64_source))
        if 'str' in aa:
            base64_source = bytes(base64_source, 'utf-8')

        return 'data:image/%s;base64,%s' % (
            FILETYPE_BASE64_MAGICWORD.get(base64_source[:1], 'png'),
            base64_source.decode(),
        )


    def check_reg_customer(self):
        if self.partner_id.x_studio_many2one_field_RZnWk:
            if 'Unregistered' in self.partner_id.x_studio_many2one_field_RZnWk.name:
                return self.get_unregistered_report_values()
            else:
                return self.get_registered_report_values()
        else:
            return self.get_unregistered_report_values()

    remarks_field = fields.Char(string="Remarks")

    def get_registered_report_values(self, data=None):
        ssss = ''
        address = ''
        date_inv = ''
        inv = []
        deli = []
        article = ''
        art_no = ''
        list_pro_color_data = []
        partner_detail = []
        color_val_name = []
        size_val_name = []
        color_name = []
        size_name = []
        pro_name = []
        product_product = []
        remarks = ''

        # name = self.env['sale.order'].search([('invoice_ids', '=', self.id)]).name
        # invoice_id = self.env['account.move'].search([('id', '=', self.id)])
        # picking_ids = self.env['sale.order'].search([('invoice_ids', '=', self.id)]).picking_ids
        # product_id = self.env['account.move'].search([('id', '=', self.id)]).invoice_line_ids
        # pro_temp_id = self.env['account.move'].search(
        #     [('id', '=', self.id)]).invoice_line_ids.product_id.product_tmpl_id

        name = self.env['sale.order'].search([('id', '=', self.id)]).name
        invoice_id = self.env['sale.order'].search([('id', '=', self.id)])
        # picking_ids = self.env['sale.order'].search([('invoice_ids', '=', self.id)]).picking_ids
        product_id = self.env['sale.order'].search([('id', '=', self.id)]).order_line
        pro_temp_id = self.env['sale.order'].search(
            [('id', '=', self.id)]).order_line.product_id.product_tmpl_id
        if invoice_id:
            inv.append(invoice_id.name)
            date_inv = invoice_id.date_order.strftime('%d-%m-%Y')
            remarks = invoice_id.remarks_field
        # if picking_ids:
        #     for i in picking_ids:
        #         deli.append(i.name)
        for pro in pro_temp_id:
            pro_name.append(pro)
            pro_atribute = pro.attribute_line_ids
            for pro_at in pro_atribute:
                pro_val = pro_at.value_ids
                for p_val in pro_val:
                    if pro_at.attribute_id.name == 'Color':
                        if not p_val.name in color_name:
                            color_name.append(p_val.name)

                    elif pro_at.attribute_id.name == 'Size':
                        if not p_val.name in size_name:
                            size_name.append(p_val.name)
        for p in product_id:
            product_product.append(p.name)
            value = p.product_id.product_template_attribute_value_ids
            for ve in value:
                attr = p.product_id.attribute_line_ids
                for a in attr:
                    val = a.value_ids
                    for v in val:
                        if not v.name in color_val_name and v.name == ve.name:
                            if v.name in color_name:
                                color_val_name.append(v.name)
                        if not v.name in size_val_name and v.name == ve.name:
                            if v.name in size_name:
                                size_val_name.append(v.name)
                                size_val_name.sort()

        taxed_amount = 0
        for pro in pro_temp_id:
            pro_name_color = []
            taxed_amount = 0
            for col in color_val_name:
                color_wise_size = []
                color_in_line = []
                price = ''
                taxed_amount = 0
                sub_total = 0
                for s in size_val_name:
                    for product in product_product:
                        for p in product_id:
                            if p.name == product and p.product_id.name == pro.name:
                                value = p.product_id.product_template_attribute_value_ids
                                for ve in value:
                                    if ve.name in color_val_name:
                                        if ve.name == col:
                                            for v_a in value:
                                                if v_a.name == s:
                                                    ssss = v_a.name
                                                    if ve.name != color_in_line:
                                                        color_in_line = ve.name
                                                    if len(str(int(p.product_uom_qty))) == 1:
                                                        color_wise_size.append('0' + str(int(p.product_uom_qty)))
                                                    else:
                                                        color_wise_size.append(str(int(p.product_uom_qty)))
                                                    price = p.price_unit
                                                    if p.tax_id:
                                                        for t in p.tax_id:
                                                            taxed_amount += t.amount * p.price_unit / 100 * p.product_uom_qty
                                                    sub_total += p.price_unit * p.product_uom_qty
                                article = p.product_id.product_tmpl_id.name
                                art_no = p.product_id.product_tmpl_id.description_pickingout

                    if ssss != s:
                        color_wise_size.append('00')
                total_qty = 0
                for cz in color_wise_size:
                    if cz:
                        total_qty = total_qty + int(cz)
                # sub_total = total_qty * price
                tax_amount = ''
                if sub_total:
                    tax_amount = taxed_amount
                inc_amount = sub_total + taxed_amount
                if color_in_line:
                    pro_name_color.append({
                        'color_in_line': color_in_line,
                        'color_wise_size': color_wise_size,
                        'unit_price': price,
                        'total_qty': total_qty,
                        'sub_total': sub_total,
                        'tax_amount': tax_amount,
                        'inc_amount': inc_amount,
                    })
            list_pro_color_data.append({
                'art_no': art_no,
                'article': article,
                'pro_name_color': pro_name_color,
            })
        if invoice_id.partner_id.street:
            address = address + ' ' + invoice_id.partner_id.street
        if invoice_id.partner_id.street2:
            address = address + ' ' + invoice_id.partner_id.street2
        if invoice_id.partner_id.city:
            address = address + ' ' + invoice_id.partner_id.city
        if invoice_id.partner_id.state_id:
            address = address + ' ' + invoice_id.partner_id.state_id.name
        if invoice_id.partner_id.zip:
            address = address + ' ' + invoice_id.partner_id.zip
        if invoice_id.partner_id.country_id:
            address = address + ' ' + invoice_id.partner_id.country_id.name
        partner_detail.append({
            'name': invoice_id.partner_id.name,
            'address': address,
        })
        test = 'Mohsan Raza'
        data = {
            'remarks': remarks,
            'so_no': name,
            # 'inv_no': inv,
            # 'deli': deli,
            'tax_id': invoice_id.partner_id.vat,
            'ntn': invoice_id.partner_id.ntn1,
            'date': date_inv,
            'partner_id': partner_detail,
            'size': size_val_name,
            'doc_model': self.env['sale.order'],
            'docs': self.env['sale.order'].browse(data),
            'lis_pro': list_pro_color_data,
        }

        return self.env.ref('wej_sale_order.action_report_sale_order_tax').report_action(self, data=data)

    def get_unregistered_report_values(self, data=None):
        ssss = ''
        address = ''
        article = ''
        list_pro_color_data = []
        inv = []
        partner_detail = []
        deli = []
        color_val_name = []
        size_val_name = []
        color_name = []
        size_name = []
        pro_name = []
        product_product = []
        name = self.env['sale.order'].search([('id', '=', self.id)]).name
        invoice_id = self.env['sale.order'].search([('id', '=', self.id)])
        # picking_ids = self.env['sale.order'].search([('invoice_ids', '=', self.id)]).picking_ids
        product_id = self.env['sale.order'].search([('id', '=', self.id)]).order_line
        pro_temp_id = self.env['sale.order'].search(
            [('id', '=', self.id)]).order_line.product_id.product_tmpl_id
        if invoice_id:
            inv.append(invoice_id.name)
            date = invoice_id.date_order.strftime('%d-%m-%Y')
            remarks = invoice_id.remarks_field
        # if picking_ids:
        #     for i in picking_ids:
        #         deli.append(i.name)
        for pro in pro_temp_id:
            pro_name.append(pro)
            pro_atribute = pro.attribute_line_ids
            for pro_at in pro_atribute:
                pro_val = pro_at.value_ids
                for p_val in pro_val:
                    if pro_at.attribute_id.name == 'Color':
                        if not p_val.name in color_name:
                            color_name.append(p_val.name)

                    elif pro_at.attribute_id.name == 'Size':
                        if not p_val.name in size_name:
                            size_name.append(p_val.name)
        for p in product_id:
            product_product.append(p.name)
            value = p.product_id.product_template_attribute_value_ids
            for ve in value:
                attr = p.product_id.attribute_line_ids
                for a in attr:
                    val = a.value_ids
                    for v in val:
                        if not v.name in color_val_name and v.name == ve.name:
                            if v.name in color_name:
                                color_val_name.append(v.name)
                        if not v.name in size_val_name and v.name == ve.name:
                            if v.name in size_name:
                                size_val_name.append(v.name)
                                size_val_name.sort()
        for pro in pro_temp_id:
            pro_name_color = []
            for col in color_val_name:
                color_wise_size = []
                color_in_line = []
                price = ''
                sub_total = 0
                for s in size_val_name:
                    for product in product_product:
                        for p in product_id:
                            if p.name == product and p.product_id.name == pro.name:
                                value = p.product_id.product_template_attribute_value_ids
                                for ve in value:
                                    if ve.name in color_val_name:
                                        if ve.name == col:
                                            for v_a in value:
                                                if v_a.name == s:
                                                    ssss = v_a.name
                                                    if ve.name != color_in_line:
                                                        color_in_line = ve.name
                                                    if len(str(int(p.product_uom_qty))) == 1:
                                                        color_wise_size.append('0' + str(int(p.product_uom_qty)))
                                                    else:
                                                        color_wise_size.append(str(int(p.product_uom_qty)))
                                                    price = p.price_unit
                                                    sub_total += p.price_unit * p.product_uom_qty
                                article = p.product_id.product_tmpl_id.name
                    if ssss != s:
                        color_wise_size.append('00')
                total_qty = 0
                for cz in color_wise_size:
                    if cz:
                        total_qty = total_qty + int(cz)
                # sub_total = total_qty * price
                if color_in_line:
                    pro_name_color.append({
                        'name': pro.name,
                        'color_in_line': color_in_line,
                        'color_wise_size': color_wise_size,
                        'unit_price': price,
                        'total_qty': total_qty,
                        'sub_total': sub_total,
                    })
            list_pro_color_data.append({
                'article': article,
                'pro_name_color': pro_name_color,
                'image': pro.image_1920,
            })
        if invoice_id.partner_id.street:
            address = address + ' ' + invoice_id.partner_id.street
        if invoice_id.partner_id.street2:
            address = address + ' ' + invoice_id.partner_id.street2
        if invoice_id.partner_id.city:
            address = address + ' ' + invoice_id.partner_id.city
        if invoice_id.partner_id.state_id:
            address = address + ' ' + invoice_id.partner_id.state_id.name
        if invoice_id.partner_id.zip:
            address = address + ' ' + invoice_id.partner_id.zip
        if invoice_id.partner_id.country_id:
            address = address + ' ' + invoice_id.partner_id.country_id.name
        partner_detail.append({
            'name': invoice_id.partner_id.name,
            'address': address,
        })
        test = 'Mohsan Raza'
        # pass
        data = {
            'remarks': remarks,
            'so_no': name,
            # 'inv_no': inv,
            'date': date,
            'doc_ids': self.id,
            'partner_id': partner_detail,
            'size': size_val_name,
            'doc_model': self.env['sale.order'],
            'docs': self.env['sale.order'].browse(data),
            'lis_pro': list_pro_color_data,
        }
        return self.env.ref('wej_sale_order.action_report_unregistered_sale_tax').report_action(self, data=data)
