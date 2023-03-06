from odoo import models, fields, api


class SaleReportWej(models.AbstractModel):
    _inherit = 'purchase.order'
    _description = 'Sale Invoice Report'

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

        order_id = self.env['purchase.order'].search([('id', '=', self.id)])
        picking_ids = self.env['purchase.order'].search([('id', '=', self.id)]).picking_ids
        product_id = self.env['purchase.order'].search([('id', '=', self.id)]).order_line
        pro_temp_id = self.env['purchase.order'].search(
            [('id', '=', self.id)]).order_line.product_id.product_tmpl_id
        if order_id:
            inv.append(order_id.name)
            date_inv = order_id.date_approve.strftime('%d-%m-%Y')
            remarks = order_id.remarks_field
        if picking_ids:
            for i in picking_ids:
                deli.append(i.name)
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
                                                    if len(str(int(p.product_qty))) == 1:
                                                        color_wise_size.append('0' + str(int(p.product_qty)))
                                                    else:
                                                        color_wise_size.append(str(int(p.product_qty)))
                                                    price = p.price_unit
                                                    if p.tax_ids:
                                                        for t in p.tax_ids:
                                                            taxed_amount += t.amount * p.price_unit / 100 * p.product_qty
                                                    sub_total += p.price_unit * p.product_qty
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
                'image': pro.image_1920,
            })
        if order_id.partner_id.street:
            address = address + ' ' + order_id.partner_id.street
        if order_id.partner_id.street2:
            address = address + ' ' + order_id.partner_id.street2
        if order_id.partner_id.city:
            address = address + ' ' + order_id.partner_id.city
        if order_id.partner_id.state_id:
            address = address + ' ' + order_id.partner_id.state_id.name
        if order_id.partner_id.zip:
            address = address + ' ' + order_id.partner_id.zip
        if order_id.partner_id.country_id:
            address = address + ' ' + order_id.partner_id.country_id.name
        partner_detail.append({
            'name': order_id.partner_id.name,
            'address': address,
        })
        test = 'Mohsan Raza'
        data = {
            'remarks': remarks,
            'name': self.name,
            'tax_id': order_id.partner_id.vat,
            'ntn': order_id.partner_id.ntn1,
            'date': date_inv,
            'partner_id': partner_detail,
            'size': size_val_name,
            'doc_model': self.env['purchase.order'],
            'docs': self.env['purchase.order'].browse(data),
            'lis_pro': list_pro_color_data,
        }

        return self.env.ref('wej_purchase_order.action_purchase_order_taxed').report_action(self, data=data)

    def get_unregistered_report_values(self, data=None):
        ssss = ''
        address = ''
        article = ''
        remarks = ''
        list_pro_color_data = []
        partner_detail = []
        deli = []
        color_val_name = []
        size_val_name = []
        color_name = []
        size_name = []
        pro_name = []
        product_product = []
        order_id = self.env['purchase.order'].search([('id', '=', self.id)])
        picking_ids = self.env['purchase.order'].search([('id', '=', self.id)]).picking_ids
        product_id = self.env['purchase.order'].search([('id', '=', self.id)]).order_line
        pro_temp_id = self.env['purchase.order'].search(
            [('id', '=', self.id)]).order_line.product_id.product_tmpl_id
        if order_id:
            remarks = order_id.remarks_field
        if picking_ids:
            for i in picking_ids:
                deli.append(i.name)
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
                                                    if len(str(int(p.product_qty))) == 1:
                                                        color_wise_size.append('0' + str(int(p.product_qty)))
                                                    else:
                                                        color_wise_size.append(str(int(p.product_qty)))
                                                    price = p.price_unit
                                                    sub_total += p.price_unit * p.product_qty
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
        if order_id.partner_id.street:
            address = address + ' ' + order_id.partner_id.street
        if order_id.partner_id.street2:
            address = address + ' ' + order_id.partner_id.street2
        if order_id.partner_id.city:
            address = address + ' ' + order_id.partner_id.city
        if order_id.partner_id.state_id:
            address = address + ' ' + order_id.partner_id.state_id.name
        if order_id.partner_id.zip:
            address = address + ' ' + order_id.partner_id.zip
        if order_id.partner_id.country_id:
            address = address + ' ' + order_id.partner_id.country_id.name
        partner_detail.append({
            'name': order_id.partner_id.name,
            'address': address,
        })
        test = 'Mohsan Raza'
        # pass
        data = {
            'remarks': remarks,
            'name': self.name,
            'doc_ids': self.id,
            'partner_id': partner_detail,
            'size': size_val_name,
            'doc_model': self.env['purchase.order'],
            'docs': self.env['purchase.order'].browse(data),
            'lis_pro': list_pro_color_data,
        }
        return self.env.ref('wej_purchase_order.action_report_purchase_order_untaxed').report_action(self, data=data)

