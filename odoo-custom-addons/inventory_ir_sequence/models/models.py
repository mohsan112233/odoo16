from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, MissingError


class CodDispersal(models.Model):
    _inherit = 'product.category'
    product_category_code = fields.Char(string='Code', required=True)
    code_duplicate = fields.Char(string='Code 2')

    @api.constrains('product_category_code')
    def code_change(self):
        if self.product_category_code:
            self.code_duplicate = self.product_category_code


class productCodetemplate(models.Model):
    _inherit = 'product.template'

    #
    # def copy(self,default= {}):
    #     print('vkfvmkfv')
    #     default['default_code'] = ''

    @api.model
    def create(self, vals_list):

        print(vals_list)
        print(vals_list['name'])
        name = vals_list['name']
        prod = self.env['product.template'].search([('name', '=', name)])

        if prod or not prod:
            id = super(productCodetemplate, self).create(vals_list)
            print('kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk', id.val)
            code_list = []
            co_list = []
            print('lppppppppppppppllllllll')
            prod = self.env['product.product'].search([('default_code', '!=', False),('categ_id.product_category_code','!=',False)])

            for i in prod:
                d = 0
                z = 0
                for a in i.default_code:
                    d = d + 1
                    if a == '-':
                        z = d
                i.default_code
                try:
                    # print(i.default_code.find('-'))
                    lis = list(i.default_code)
                    index = lis.index('-', -8, -1)
                    st = (lis[0:index])
                except:
                    raise ValidationError(f"{i.name} have code without dash")
                emptystr = ""
                # passing in a string
                for e in st:
                    emptystr += e
                # ls = i.default_code[:z-1]
                # print(ls)
                if emptystr:
                    emptystr = emptystr + str(id.val)
                code_list.append({i.id: emptystr})
                a = 0
                l = len(i.default_code)

            print('sasad2', id.default_code)
            if not id.default_code:
                # id.default_code = self.env['ir.sequence'].next_by_code('product.product.code') or 'New'
                code = id.categ_id.product_category_code
                if id.categ_id.parent_id:
                    if id.categ_id.parent_id:
                        if code and id.categ_id.parent_id.product_category_code:
                            code = code + '-' + id.categ_id.parent_id.product_category_code
                    if id.categ_id.parent_id.parent_id:
                        if code and id.categ_id.parent_id.parent_id.product_category_code:
                            code = code + '-' + id.categ_id.parent_id.parent_id.product_category_code
                    if id.categ_id.parent_id.parent_id.parent_id:
                        if code and id.categ_id.parent_id.parent_id.parent_id.product_category_code:
                            code = code + '-' + id.categ_id.parent_id.parent_id.parent_id.product_category_code
                print(code_list,'psppekdkdkd')
                for co in code_list:
                    new_list = list(co.values())

                    new_list1 = list(co.keys())
                    # print(new_list[0])
                    print('ffffffffffdddddddddddddd')
                    print(new_list[0],code)
                    if new_list[0] == str(code) +'-'+ str(id.val):
                        co_list.append(new_list1[0])

                if co_list:
                    print(co_list)
                    ma = max(co_list)
                    prod = self.env['product.product'].search([
                                                           ('ma', '=',ma)])
                    print('lllllllld47886533',prod)

                    f_list = list(prod.default_code)

                    f_list = (f_list[-6:])
                    emptystr = ""
                    # passing in a string
                    for e in f_list:
                        emptystr += e
                    print(f_list, emptystr)
                    if emptystr:
                        last_no = int(emptystr)
                        last_no = last_no + 1
                        last_no = str(last_no)
                        if len(last_no) == 1:
                            last_no = '00000' + last_no
                        if len(last_no) == 2:
                            last_no = '0000' + last_no
                        if len(last_no) == 3:
                            last_no = '000' + last_no
                        if len(last_no) == 4:
                            last_no = '00' + last_no
                        if len(last_no) == 5:
                            last_no = '0' + last_no
                        print(code, last_no)
                        print(id.default_code, 'lpl')
                        print('ddddddddddddddddddddddddd')
                        # sql = ("UPDATE product_produc SET default_code=%s WHERE id=%s")
                        # self.env.cr.execute(sql, (default_code, id.id))
                        # self.env.cr.commit()
                        b = 0
                        for i in id.attribute_line_ids:

                            if i.value_ids:
                                print(len(i.value_ids), 'ppppppppppppppeee')
                                if len(i.value_ids) > 1:
                                    b = 1
                        print(id.default_code,'okcnsncjnsn')
                        if b == 0:
                            print('saadddddddd')
                            id.default_code = code + '-' + id.val + '-' + last_no
                            default_code = code + '-' + id.val + '-' + last_no

                            id.write({'default_code': default_code})
                            print(id.default_code)
                        # if not id.product_tmpl_id.default_code:
                        #     id.product_tmpl_id.default_code = default_code
                else:
                    if code:
                        b = 0
                        for i in id.attribute_line_ids:

                            if i.value_ids:
                                print(len(i.value_ids), 'ppppppppppppppeee')
                                if len(i.value_ids) > 1:
                                    b = 1
                        if b == 0:
                            id.default_code = code + '-' +id.val+ '-' + '000001'
                            default_code = code + '-' + id.val + '-' + '000001'
                            # sql = ("UPDATE product_product SET default_code=%s WHERE id=%s")
                            # self.env.cr.execute(sql, (default_code, id.id))
                            # self.env.cr.commit()
                            id.write({'default_code': default_code})
                            # if not id.product_tmpl_id.default_code:
                            #     id.product_tmpl_id.default_code = default_code
            return id


class productCode(models.Model):
    _inherit = 'product.product'
    product_code_id = fields.Char(string='Code')
    check = fields.Char(string='check', default='Uncheck')

    def check_field(self):
        active_id = self.env['product.product'].browse(self.env.context.get('active_ids', []))
        active_id.write({'check': 'Checked'})

    def copy(self, default={}):
        default['default_code'] = ''

    @api.model
    def create(self, vals_list):


        id = super(productCode, self).create(vals_list)
        c = id.product_tmpl_id
        if c.fg == True and c.raw == False:

            c.val = c.season_id.description + '-' + c.origin_id.description + '-' + c.type_id.description + '-' \
                  + c.market_id.description + '-' + c.brands_id.description
            print(c.val)
            strs = ''

            # return c.val
        if c.fg == False and c.raw == True:
            c.val = c.make_id.description + '-' + c.artical_market_code.description
            print(c.val)
            # return c.val
        code_list = []
        co_list = []
        print('lppppppppppppppllllllll')
        prod = self.env['product.product'].search([('default_code', '!=', False),('categ_id.product_category_code','!=',False)])

        for i in prod:
            d = 0
            z = 0
            for a in i.default_code:
                d = d + 1
                if a == '-':
                    z = d
            i.default_code
            try:
                # print(i.default_code.find('-'))
                lis = list(i.default_code)
                index = lis.index('-', -8, -1)
                st = (lis[0:index])
            except:
                raise ValidationError(f"{i.name} have code without dash")
            emptystr = ""
            # passing in a string
            for e in st:
                emptystr += e
            if emptystr:
                str(emptystr) + str(id.product_tmpl_id.val)
            # ls = i.default_code[:z-1]
            # print(ls)
            code_list.append({i.id: emptystr})
            a = 0
            l = len(i.default_code)

        print('sasad', id.default_code)
        if not id.default_code:
            # id.default_code = self.env['ir.sequence'].next_by_code('product.product.code') or 'New'
            code = id.categ_id.product_category_code
            if id.categ_id.parent_id:
                if id.categ_id.parent_id:
                    if code and id.categ_id.parent_id.product_category_code:
                        code = code + '-' + id.categ_id.parent_id.product_category_code
                if id.categ_id.parent_id.parent_id:
                    if code and id.categ_id.parent_id.parent_id.product_category_code:
                        code = code + '-' + id.categ_id.parent_id.parent_id.product_category_code
                if id.categ_id.parent_id.parent_id.parent_id:
                    if code and id.categ_id.parent_id.parent_id.parent_id.product_category_code:
                        code = code + '-' + id.categ_id.parent_id.parent_id.parent_id.product_category_code
            print(code_list, 'psppekdkdkd')
            prod = self.env['product.product'].search([
                ('default_code', 'like', str(code) + str(id.product_tmpl_id.val))], limit=1, order="id desc")
            print('lllllllld47886533', prod)

            for co in code_list:
                new_list = list(co.values())

                new_list1 = list(co.keys())
                # print(new_list[0])
                print(str(new_list[0]),str(code) +'-'+ str(id.product_tmpl_id.val))
                if new_list[0] == str(code) + '-'+str(id.product_tmpl_id.val):
                    co_list.append(new_list1[0])

            if co_list:
                print(co_list)
                ma = max(co_list)
                prod = self.env['product.product'].search([
                                                           ('id', '=', ma)])
                print('lllllllld47886533',prod)

                f_list = list(prod.default_code)

                f_list = (f_list[-6:])
                emptystr = ""
                # passing in a string
                for e in f_list:
                    emptystr += e
                print(f_list, emptystr)
                if emptystr:
                    last_no = int(emptystr)
                    last_no = last_no + 1
                    last_no = str(last_no)
                    if len(last_no) == 1:
                        print('val....', self.product_tmpl_id.val)
                        last_no = '00000' + last_no
                    if len(last_no) == 2:
                        last_no = '0000' + last_no
                    if len(last_no) == 3:
                        last_no = '000' + last_no
                    if len(last_no) == 4:
                        last_no = '00' + last_no
                    if len(last_no) == 5:
                        last_no = '0' + last_no
                    print(code, last_no)
                    print(id.default_code, 'lpl')
                    print(id.val)
                    val = id.product_tmpl_id.val
                    print(id.product_tmpl_id.name)
                    print(val)
                    id.default_code = code + '-' + val + '-' + last_no
                    default_code = code + '-' + val + '-' + last_no

                    sql = ("UPDATE product_product SET default_code=%s WHERE id=%s")
                    self.env.cr.execute(sql, (default_code, id.id))
                    self.env.cr.commit()

                    id.write({'default_code': default_code})
                    print(id.default_code)
                    # if not id.default_code:
                    #     print('work', id.product_tmpl_id.default_code)
                    #     id.default_code = id.product_tmpl_id.default_code
            else:
                if code:
                    val = id.product_tmpl_id.val
                    # id.default_code = code + '-' + val + '-' + last_no
                    id.default_code = code +'-'+ val +'-' + '000001'
                    default_code = code +'-'+ val +'-' + '000001'
                    sql = ("UPDATE product_product SET default_code=%s WHERE id=%s")
                    self.env.cr.execute(sql, (default_code, id.id))
                    self.env.cr.commit()
                    id.write({'default_code': default_code})
                    if not id.default_code:
                        id.default_code = id.product_tmpl_id.default_code
        return id

    def change_bulk_code(self):
        print('ddddddddddddsssssssss')
        cat_list = []
        prod_bulk = self.env['product.product'].search([('check', '=', 'Checked')
                                                        ])
        print('lllldd', prod_bulk)
        for cat in prod_bulk:
            cat_list.append(cat.categ_id.id)
        new_list = list(set(cat_list))
        print(new_list)
        for i in new_list:
            code_list = []
            co_list = []
            prod = self.env['product.product'].search([('categ_id.id', '=', i)
                                                       ], order='id asc')
            print(prod)
            last_no = 0
            for id in prod:
                id.write({'check': 'Unchecked'})
                # id.default_code = self.env['ir.sequence'].next_by_code('product.product.code') or 'New'
                code = id.categ_id.product_category_code
                if id.categ_id.parent_id:
                    if code and id.categ_id.parent_id.product_category_code:
                        code = code + '-' + id.categ_id.parent_id.product_category_code
                if id.categ_id.parent_id.parent_id:
                    if code and id.categ_id.parent_id.parent_id.product_category_code:
                        code = code + '-' + id.categ_id.parent_id.parent_id.product_category_code
                if id.categ_id.parent_id.parent_id.parent_id:
                    if code and id.categ_id.parent_id.parent_id.parent_id.product_category_code:
                        code = code + '-' + id.categ_id.parent_id.parent_id.parent_id.product_category_code
                if code:
                    last_no = last_no + 1
                    last_no1 = str(last_no)
                    if len(last_no1) == 1:
                        last_no = '00000' + last_no1
                    if len(last_no1) == 2:
                        last_no = '0000' + last_no1
                    if len(last_no1) == 3:
                        last_no = '000' + last_no1
                    if len(last_no1) == 4:
                        last_no = '00' + last_no1
                    if len(last_no1) == 5:
                        last_no = '0' + last_no1
                    c = id.product_tmpl_id.val
                    id.default_code = code +'-'+c +'-' + last_no
                    last_no = int(last_no)
            # else:
            #     if code:
            #         id.default_code = code + '-' + '000001'
            #         print(self.default_code)
            #
            #     # for co in code_list:
            #     new_list = list(co.values())
            #
            #     new_list1 = list(co.keys())
            #
            #     if new_list[0] == code:
            #         co_list.append(new_list1[0])
            #
            # if co_list:
            #     print(co_list)
            #     ma = max(co_list)
            #     prod = self.env['product.product'].search([('id', '=', ma)])
            #     f_list = list(prod.default_code)
            #     f_list = (f_list[-6:])
            #     emptystr = ""
            #     # passing in a string
            #     for e in f_list:
            #         emptystr += e
            #
            #     if emptystr:
            #
            #         last_no = int(emptystr)
            #         last_no = last_no + 1
            #         last_no1 = str(last_no)
            #         if len(last_no1) == 1:
            #             last_no = '00000' + last_no1
            #         if len(last_no1) == 2:
            #             last_no = '0000' + last_no1
            #         if len(last_no1) == 3:
            #             last_no = '000' + last_no1
            #         if len(last_no1) == 4:
            #             last_no = '00' + last_no1
            #         if len(last_no1) == 5:
            #             last_no = '0' + last_no1
            #         id.default_code = code + '-' + last_no
            #
            # else:
            #     if code:
            #         id.default_code = code + '-' + '000001'
            #         print(self.default_code)
            #
            #
            #
