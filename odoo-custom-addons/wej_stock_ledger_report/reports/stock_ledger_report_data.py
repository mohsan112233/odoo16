from odoo import models, fields, api
from multiprocessing import Process
import time
import io
import logging
import pytz
from datetime import datetime

_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
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


class WejStockLedgerReportWiz(models.TransientModel):
    _name = 'wej.stock.ledger.report.wiz'
    _description = 'Wej Stock Ledger Report Wizard'

    categ_id = fields.Many2one('product.category', string="Category")
    article = fields.Many2one('product.template', string="Article")
    color_id = fields.Many2one('product.attribute.value', string='Color')
    warehouse_id = fields.Many2one('stock.warehouse', string="Location")
    inventory_datetime = fields.Datetime('Date',
                                         help="Choose a date to get the inventory at that date",
                                         default=fields.datetime.now())

    # def get_report_with_price_xlsx(self):
    #     data = []
    #     p = Process(target=self.get_report_value(data))
    #     # start = time.time()
    #     p.start()
    #     p.join()
    #     data = {
    #         'data': data,
    #     }
    #     # end = time.time()
    def get_report_with_price(self):
        data = []
        p = Process(target=self.get_report_value(data))
        p.start()
        p.join()
        rec = {
            'data': data,
        }
        return self.env.ref('wej_stock_ledger_report.action_report_stock_report').report_action(self, data=rec)

    def get_report_without_price(self):
        data = []
        p = Process(target=self.get_report_value(data))
        # start = time.time()
        p.start()
        p.join()
        rec = {
            'data': data,
        }
        # end = time.time()
        return self.env.ref('wej_stock_ledger_report.action_report_stock_report2').report_action(self, data=rec)

    def get_report_value(self, data):
        domain = []
        if self.article:
            domain.append(('name', '=', self.article.name))
        if self.categ_id:
            domain.append(('categ_id', '=', self.categ_id.id))
        # if self.warehouse_id:
        #     domain.append(('warehouse_id', '=', self.warehouse_id.id))
        if domain:
            pro_temp_id = self.env['product.template'].search(domain)
        else:
            pro_temp_id = self.env['product.template'].search([('id', '!=', False)])
        color_ids = self.env['product.attribute'].search([('name', '=', 'Color')])
        size_ids = self.env['product.attribute'].search([('name', '=', 'Size')])
        ssss = ''
        article = ''
        list_pro_color_data = []
        color_name = []
        size_name = []
        pro_name = []
        grand_total = []
        for ci in color_ids.value_ids:
            if not ci.name in color_name:
                color_name.append(ci.name)
        for si in size_ids.value_ids.sorted(key=lambda r: r.name, reverse=False):
            if not si.name in size_name:
                size_name.append(si.name)
        size_name.sort()
        lenth = len(size_name)
        if self.color_id:
            color_name = [self.color_id.name]
        price = ''
        inventory_datetime = self.inventory_datetime.astimezone(pytz.timezone('Asia/Karachi'))
        inventory_datetime = inventory_datetime.strftime('%Y-%m-%d %H:%M:%S')
        for pro in pro_temp_id:
            print(pro.name)
            pro_name.append(pro)
            product_id = self.env['product.product'].search([('product_tmpl_id', '=', pro.id)]).with_context(
                to_datetime=inventory_datetime, warehouse=self.warehouse_id.id)
            if product_id:
                pro_name_color = []
                sub_total_artical = []
                sub_total_price = 0
                sub_total = 0
                sub_total_amount = 0
                for col in color_name:
                    color_wise_size = []
                    color_in_line = []
                    price = 0
                    pr_count = 0
                    for s in size_name:
                        for p in product_id:
                            value = p.product_template_attribute_value_ids
                            for ve in value:
                                if ve.name == col:
                                    for v_a in value:
                                        if v_a.name == s:
                                            ssss = v_a.name
                                            if ve.name != color_in_line:
                                                color_in_line = ve.name
                                            color_wise_size.append(
                                                p.qty_available)
                                            sub_total += p.qty_available * p.standard_price
                                            price += p.standard_price
                                            pr_count += 1
                            article = p.product_tmpl_id.name
                        if ssss != s:
                            color_wise_size.append(0)
                    total_qty = 0
                    for cz in color_wise_size:
                        if cz:
                            total_qty = total_qty + int(cz)
                    if sum(color_wise_size) != 0:
                        _logger.info(len(color_wise_size))
                        _logger.info(color_wise_size)
                        if len(color_wise_size) == lenth:
                            for l in range(0, lenth):
                                if len(sub_total_artical) == lenth:
                                    sub_total_artical[l] += int(color_wise_size[l])
                                else:
                                    sub_total_artical.append(int(color_wise_size[l]))
                                if len(grand_total) == lenth:
                                    grand_total[l] += int(color_wise_size[l])
                                else:
                                    grand_total.append(int(color_wise_size[l]))
                    if pr_count == 0:
                        pr_count = 1
                    price = price / pr_count
                    if price == 0:
                        sub_total = 0
                    sub_total_price += price
                    if total_qty != 0:
                        sub_total_amount += sub_total
                        if color_in_line:
                            pro_name_color.append({
                                'name': pro.name,
                                'color_in_line': color_in_line,
                                'color_wise_size': color_wise_size,
                                'unit_price': sub_total / total_qty,
                                'total_qty': total_qty,
                                'sub_total': sub_total,
                            })
                if sum(sub_total_artical) != 0:
                    if pro_name_color:
                        list_pro_color_data.append({
                            'article': article,
                            'pro_name_color': pro_name_color,
                            'sub_total_artical': sub_total_artical,
                            'sub_total_qty': sum(sub_total_artical),
                            'sub_total_price': sub_total_amount / sum(sub_total_artical),
                        })
        if self.categ_id.parent_id:
            if self.categ_id.parent_id.parent_id:
                if self.categ_id.parent_id.parent_id.parent_id:
                    category = self.categ_id.parent_id.parent_id.parent_id.name + ' / ' + self.categ_id.parent_id.parent_id.name + ' / ' + self.categ_id.parent_id.name + ' / ' + self.categ_id.name
                else:
                    category = self.categ_id.parent_id.parent_id.name + ' / ' + self.categ_id.parent_id.name + ' / ' + self.categ_id.name
            else:
                category = self.categ_id.parent_id.name + ' / ' + self.categ_id.name
        else:
            category = self.categ_id.name
        test = 'Mohsan Raza'
        print(test)
        return data.append({
            'color': self.color_id.name,
            'article': self.article.name,
            'category': category,
            'size': size_name,
            'warehouse': self.warehouse_id.name,
            'date': inventory_datetime,
            'grand_total': grand_total,
            'grand_total_qty': sum(grand_total),
            'lis_pro': list_pro_color_data,
        })

    def get_report_with_price_xlsx(self):
        domain = []
        if self.article:
            domain.append(('name', '=', self.article.name))
        if self.categ_id:
            domain.append(('categ_id', '=', self.categ_id.id))
        # if self.warehouse_id:
        #     domain.append(('warehouse_id', '=', self.warehouse_id.id))
        if domain:
            pro_temp_id = self.env['product.template'].search(domain)
        else:
            pro_temp_id = self.env['product.template'].search([('id', '!=', False)])
        color_ids = self.env['product.attribute'].search([('name', '=', 'Color')])
        size_ids = self.env['product.attribute'].search([('name', '=', 'Size')])
        ssss = ''
        article = ''
        list_pro_color_data = []
        color_name = []
        size_name = []
        pro_name = []
        grand_total = []
        for ci in color_ids.value_ids:
            if not ci.name in color_name:
                color_name.append(ci.name)
        for si in size_ids.value_ids.sorted(key=lambda r: r.name, reverse=False):
            if not si.name in size_name:
                size_name.append(si.name)
        lenth = len(size_name)
        if self.color_id:
            color_name = [self.color_id.name]
        price = ''
        inventory_datetime = self.inventory_datetime.astimezone(pytz.timezone('Asia/Karachi'))
        inventory_datetime = inventory_datetime.strftime('%Y-%m-%d %H:%M:%S')
        for pro in pro_temp_id:
            pro_name.append(pro)
            product_id = self.env['product.product'].search([('product_tmpl_id', '=', pro.id)]).with_context(
                to_datetime=inventory_datetime, warehouse=self.warehouse_id.id)
            if product_id:
                pro_name_color = []
                sub_total_artical = []
                sub_total_price = 0
                sub_total = 0
                sub_total_amount = 0
                for col in color_name:
                    color_wise_size = []
                    color_in_line = []
                    price = 0
                    pr_count = 0
                    for s in size_name:
                        for p in product_id:
                            value = p.product_template_attribute_value_ids
                            for ve in value:
                                if ve.name == col:
                                    for v_a in value:
                                        if v_a.name == s:
                                            ssss = v_a.name
                                            if ve.name != color_in_line:
                                                color_in_line = ve.name
                                            color_wise_size.append(
                                                p.qty_available)
                                            sub_total += p.qty_available * p.standard_price
                                            price += p.standard_price
                                            pr_count += 1
                            article = p.product_tmpl_id.name
                        if ssss != s:
                            color_wise_size.append(0)
                    total_qty = 0
                    for cz in color_wise_size:
                        if cz:
                            total_qty = total_qty + int(cz)
                    if sum(color_wise_size) != 0:
                        _logger.info(len(color_wise_size))
                        _logger.info(color_wise_size)
                        if len(color_wise_size) == lenth:
                            for l in range(0, lenth-1):
                                if len(sub_total_artical) == lenth:
                                    sub_total_artical[l] += int(color_wise_size[l])
                                else:
                                    sub_total_artical.append(int(color_wise_size[l]))
                                if len(grand_total) == lenth:
                                    grand_total[l] += int(color_wise_size[l])
                                else:
                                    grand_total.append(int(color_wise_size[l]))
                    if pr_count == 0:
                        pr_count = 1
                    price = price / pr_count
                    if price == 0:
                        sub_total = 0
                    sub_total_price += price
                    if total_qty != 0:
                        sub_total_amount += sub_total
                        if color_in_line:
                            pro_name_color.append({
                                'name': pro.name,
                                'color_in_line': color_in_line,
                                'color_wise_size': color_wise_size,
                                'unit_price': sub_total / total_qty,
                                'total_qty': total_qty,
                                'sub_total': sub_total,
                            })
                if sum(sub_total_artical) != 0:
                    if pro_name_color:
                        list_pro_color_data.append({
                            'article': article,
                            'pro_name_color': pro_name_color,
                            'sub_total_artical': sub_total_artical,
                            'sub_total_qty': sum(sub_total_artical),
                            'sub_total_price': sub_total_amount / sum(sub_total_artical),
                        })
        if self.categ_id.parent_id:
            if self.categ_id.parent_id.parent_id:
                if self.categ_id.parent_id.parent_id.parent_id:
                    category = self.categ_id.parent_id.parent_id.parent_id.name + ' / ' + self.categ_id.parent_id.parent_id.name + ' / ' + self.categ_id.parent_id.name + ' / ' + self.categ_id.name
                else:
                    category = self.categ_id.parent_id.parent_id.name + ' / ' + self.categ_id.parent_id.name + ' / ' + self.categ_id.name
            else:
                category = self.categ_id.parent_id.name + ' / ' + self.categ_id.name
        else:
            category = self.categ_id.name
        test = 'Mohsan Raza'
        data = {
            'color': self.color_id.name,
            'article': self.article.name,
            'category': category,
            'size': size_name,
            'warehouse': self.warehouse_id.name,
            'date': inventory_datetime,
            'grand_total': grand_total,
            'grand_total_qty': sum(grand_total),
            'lis_pro': list_pro_color_data,
        }
        return self.env.ref('wej_stock_ledger_report.report_stock_ledger_price_excel').report_action([], data=data)

    def get_report_without_price_xlsx(self):
        domain = []
        if self.article:
            domain.append(('name', '=', self.article.name))
        if self.categ_id:
            domain.append(('categ_id', '=', self.categ_id.id))
        # if self.warehouse_id:
        #     domain.append(('warehouse_id', '=', self.warehouse_id.id))
        if domain:
            pro_temp_id = self.env['product.template'].search(domain)
        else:
            pro_temp_id = self.env['product.template'].search([('id', '!=', False)])
        color_ids = self.env['product.attribute'].search([('name', '=', 'Color')])
        size_ids = self.env['product.attribute'].search([('name', '=', 'Size')])
        ssss = ''
        article = ''
        list_pro_color_data = []
        color_name = []
        size_name = []
        pro_name = []
        grand_total = []
        for ci in color_ids.value_ids:
            if not ci.name in color_name:
                color_name.append(ci.name)
        for si in size_ids.value_ids.sorted(key=lambda r: r.name, reverse=False):
            if not si.name in size_name:
                size_name.append(si.name)
        lenth = len(size_name)
        if self.color_id:
            color_name = [self.color_id.name]
        price = ''
        inventory_datetime = self.inventory_datetime.astimezone(pytz.timezone('Asia/Karachi'))
        inventory_datetime = inventory_datetime.strftime('%Y-%m-%d %H:%M:%S')
        for pro in pro_temp_id:
            pro_name.append(pro)
            product_id = self.env['product.product'].search([('product_tmpl_id', '=', pro.id)]).with_context(
                to_datetime=inventory_datetime, warehouse=self.warehouse_id.id)
            if product_id:
                pro_name_color = []
                sub_total_artical = []
                sub_total_price = 0
                sub_total = 0
                sub_total_amount = 0
                for col in color_name:
                    color_wise_size = []
                    color_in_line = []
                    price = 0
                    pr_count = 0
                    for s in size_name:
                        for p in product_id:
                            value = p.product_template_attribute_value_ids
                            for ve in value:
                                if ve.name == col:
                                    for v_a in value:
                                        if v_a.name == s:
                                            ssss = v_a.name
                                            if ve.name != color_in_line:
                                                color_in_line = ve.name
                                            color_wise_size.append(
                                                p.qty_available)
                                            sub_total += p.qty_available * p.standard_price
                                            price += p.standard_price
                                            pr_count += 1
                            article = p.product_tmpl_id.name
                        if ssss != s:
                            color_wise_size.append(0)
                    total_qty = 0
                    for cz in color_wise_size:
                        if cz:
                            total_qty = total_qty + int(cz)
                    if sum(color_wise_size) != 0:
                        _logger.info(len(color_wise_size))
                        _logger.info(color_wise_size)
                        if len(color_wise_size) == lenth:
                            for l in range(0, lenth-1):
                                if len(sub_total_artical) == lenth:
                                    sub_total_artical[l] += int(color_wise_size[l])
                                else:
                                    sub_total_artical.append(int(color_wise_size[l]))
                                if len(grand_total) == lenth:
                                    grand_total[l] += int(color_wise_size[l])
                                else:
                                    grand_total.append(int(color_wise_size[l]))
                    if pr_count == 0:
                        pr_count = 1
                    price = price / pr_count
                    if price == 0:
                        sub_total = 0
                    sub_total_price += price
                    if total_qty != 0:
                        sub_total_amount += sub_total
                        if color_in_line:
                            pro_name_color.append({
                                'name': pro.name,
                                'color_in_line': color_in_line,
                                'color_wise_size': color_wise_size,
                                'unit_price': sub_total / total_qty,
                                'total_qty': total_qty,
                                'sub_total': sub_total,
                            })
                if sum(sub_total_artical) != 0:
                    if pro_name_color:
                        list_pro_color_data.append({
                            'article': article,
                            'pro_name_color': pro_name_color,
                            'sub_total_artical': sub_total_artical,
                            'sub_total_qty': sum(sub_total_artical),
                            'sub_total_price': sub_total_amount / sum(sub_total_artical),
                        })
        if self.categ_id.parent_id:
            if self.categ_id.parent_id.parent_id:
                if self.categ_id.parent_id.parent_id.parent_id:
                    category = self.categ_id.parent_id.parent_id.parent_id.name + ' / ' + self.categ_id.parent_id.parent_id.name + ' / ' + self.categ_id.parent_id.name + ' / ' + self.categ_id.name
                else:
                    category = self.categ_id.parent_id.parent_id.name + ' / ' + self.categ_id.parent_id.name + ' / ' + self.categ_id.name
            else:
                category = self.categ_id.parent_id.name + ' / ' + self.categ_id.name
        else:
            category = self.categ_id.name
        test = 'Mohsan Raza'
        data = {
            'color': self.color_id.name,
            'article': self.article.name,
            'category': category,
            'size': size_name,
            'warehouse': self.warehouse_id.name,
            'date': inventory_datetime,
            'grand_total': grand_total,
            'grand_total_qty': sum(grand_total),
            'lis_pro': list_pro_color_data,
        }
        return self.env.ref('wej_stock_ledger_report.report_stock_ledger_without_price_excel').report_action([],
                                                                                                             data=data)


class FinancialAnalysisReport(models.AbstractModel):
    _name = 'report.wej_stock_ledger_report.report_stock_ledger_price_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def create_xlsx_report(self, docids, data, cancel_backorder=False):
        objs = self._get_objs_for_report(docids, data)
        file_data = io.BytesIO()
        workbook = xlsxwriter.Workbook(file_data, self.get_workbook_options())
        self.pro(workbook, data, objs)
        workbook.close()
        file_data.seek(0)
        return file_data.read(), "xlsx"

    def pro(self, workbook, data, objs):
        p = Process(target=self.generate_xlsx_report(workbook, data, objs), args=('bob',))
        p.start()
        p.join()

    def generate_xlsx_report(self, workbook, data, rec):
        cell_format = workbook.add_format()
        cell_format.set_align('center')
        head_format = workbook.add_format()
        head_format.set_align('center')
        head_format.set_bold()
        head_format.set_font_size(15)
        text_wrap = workbook.add_format()
        text_wrap.set_align('center')
        text_wrap.set_bold()
        text_wrap.set_bg_color('#c8cfc9')
        text_wrap.set_text_wrap()
        text_wrap.set_border()
        text_wrap1 = workbook.add_format()
        text_wrap1.set_align('center')
        text_wrap1.set_text_wrap()
        text_wrap1.set_border()
        text_wrap2 = workbook.add_format()
        text_wrap2.set_align('center')
        text_wrap2.set_text_wrap()
        text_wrap2.set_border()
        text_wrap2.set_bold()
        text_wrap3 = workbook.add_format()
        text_wrap3.set_align('left')
        text_wrap3.set_text_wrap()
        text_wrap3.set_border()
        text_wrap3.set_bold()
        text_wrap4 = workbook.add_format()
        text_wrap4.set_align('right')
        text_wrap4.set_bold()
        text_wrap4.set_bg_color('#c8cfc9')
        text_wrap4.set_text_wrap()
        text_wrap5 = workbook.add_format()
        text_wrap5.set_align('left')
        text_wrap5.set_bold()
        text_wrap5.set_bg_color('#c8cfc9')
        text_wrap5.set_text_wrap()

        bold1 = workbook.add_format()
        bold1.set_bold()
        bold1.set_align('center')
        bold1.set_text_wrap()
        bold2 = workbook.add_format()
        bold2.set_bold()
        bold2.set_bg_color('#89b3c9')
        bold3 = workbook.add_format()
        bold3.set_bold()
        bold3.set_align('center')
        bold3.set_font_size(18)
        bold3.set_bg_color('#f7f9fa')
        bold3.set_color('#8C2586')
        bold4 = workbook.add_format()
        bold4.set_bold()
        bold4.set_bg_color('#8497a1')
        bold4.set_align('left')
        bold5 = workbook.add_format()
        bold5.set_bold()
        bold5.set_bg_color('#8497a1')
        bold5.set_align('right')

        sheet = workbook.add_worksheet('Stock Ledger XLSX')
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 20)

        sheet.merge_range(0, 0, 1, 19, self.env.company.name, bold3)
        sheet.merge_range(2, 0, 3, 19, 'Stock Ledger', head_format)
        sheet.merge_range(4, 0, 5, 1, 'Location:', bold5)
        if data['warehouse']:
            sheet.merge_range(4, 2, 5, 3, data['warehouse'], bold4)
        else:
            sheet.merge_range(4, 2, 5, 3, 'All', bold4)
        sheet.merge_range(4, 4, 5, 5, 'Category:', bold5)
        if data['category']:
            sheet.merge_range(4, 6, 5, 7, data['category'], bold4)
        else:
            sheet.merge_range(4, 6, 5, 7, 'All', bold4)
        sheet.merge_range(4, 8, 5, 9, 'Color:', bold5)
        if data['color']:
            sheet.merge_range(4, 10, 5, 11, data['color'], bold4)
        else:
            sheet.merge_range(4, 10, 5, 11, 'All', bold4)
        sheet.merge_range(4, 12, 5, 13, 'Article:', bold5)
        if data['article']:
            sheet.merge_range(4, 14, 5, 15, data['article'], bold4)
        else:
            sheet.merge_range(4, 14, 5, 15, 'All', bold4)
        sheet.merge_range(4, 16, 5, 17, 'Inventory Date:', bold5)
        sheet.merge_range(4, 18, 5, 19, data['date'], bold4)
        col = 0
        sheet.merge_range(6, 0, 7, 0, 'Sr No.', text_wrap)
        col += 1
        sheet.merge_range(6, col, 7, col, 'Article', text_wrap)
        col += 1
        sheet.merge_range(6, col, 7, col, 'Color', text_wrap)
        col += 1
        for s in data['size']:
            sheet.merge_range(6, col, 7, col, s, text_wrap)
            col += 1
        sheet.merge_range(6, col, 7, col, 'Total Qty', text_wrap)
        col += 1
        sheet.merge_range(6, col, 7, col, 'Rate', text_wrap)
        col += 1
        sheet.merge_range(6, col, 7, col, 'Amount', text_wrap)

        row = 8
        sr = 0
        grand_total_amount = 0
        for lp in data['lis_pro']:
            sr = sr + 1
            col = 0
            sheet.write(row, col, sr, text_wrap1)
            sheet.write(row, col + 1, lp['article'], text_wrap1)
            for lc in lp['pro_name_color']:
                sheet.write(row, col + 2, lc['color_in_line'], text_wrap1)
                col_size = 3
                for lsc in lc['color_wise_size']:
                    sheet.write(row, col_size, lsc, text_wrap1)
                    col_size += 1
                sheet.write(row, col_size, lc['total_qty'], text_wrap1)
                sheet.write(row, col_size + 1, round(lc['unit_price'], 2), text_wrap1)
                sheet.write(row, col_size + 2, round(lc['sub_total'], 2), text_wrap1)
                grand_total_amount += lc['sub_total']
                row = row + 1
                sheet.write(row, col + 2, 'Total', text_wrap2)
                col_size = 3
                for sta in lp['sub_total_artical']:
                    sheet.write(row, col_size, sta, text_wrap2)
                    col_size += 1
                sheet.write(row, col_size, lp['sub_total_qty'], text_wrap2)
                sheet.write(row, col_size + 1, round(lp['sub_total_price'], 2), text_wrap2)
                sheet.write(row, col_size + 2, round(lp['sub_total_qty'] * lp['sub_total_price'], 2), text_wrap2)
            row = row + 1
        row += 1
        sheet.merge_range(row, 0, row, 2, 'Grand Total', text_wrap3)
        col_size = 3
        if data['grand_total']:
            for gt in data['grand_total']:
                sheet.write(row, col_size, gt, text_wrap2)
                col_size += 1
        else:
            for gt in data['size']:
                sheet.write(row, col_size, 0, text_wrap2)
                col_size += 1
        sheet.write(row, col_size, data['grand_total_qty'], text_wrap2)
        if data['grand_total_qty'] != 0:
            sheet.write(row, col_size + 1, round(grand_total_amount / data['grand_total_qty'], 2), text_wrap2)
        else:
            sheet.write(row, col_size + 1, 0, text_wrap2)
        sheet.write(row, col_size + 2, round(grand_total_amount, 2), text_wrap2)
        sheet.merge_range(row + 2, 14, row + 2, 16, 'Generated By:', text_wrap4)
        sheet.merge_range(row + 2, 17, row + 2, 19, self.env.user.name, text_wrap5)
        sheet.merge_range(row + 3, 14, row + 3, 16, 'Printed on:', text_wrap4)
        sheet.merge_range(row + 3, 17, row + 3, 19, datetime.now().strftime("%Y/%m/%d %H:%M"),
                          text_wrap5)


class FinancialAnalysisReport(models.AbstractModel):
    _name = 'report.wej_stock_ledger_report.report_stock_without_price_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def create_xlsx_report(self, docids, data, cancel_backorder=False):
        objs = self._get_objs_for_report(docids, data)
        file_data = io.BytesIO()
        workbook = xlsxwriter.Workbook(file_data, self.get_workbook_options())
        self.pro(workbook, data, objs)
        workbook.close()
        file_data.seek(0)
        return file_data.read(), "xlsx"

    def pro(self, workbook, data, objs):
        p = Process(target=self.generate_xlsx_report(workbook, data, objs), args=('bob',))
        p.start()
        p.join()

    def generate_xlsx_report(self, workbook, data, rec):
        cell_format = workbook.add_format()
        cell_format.set_align('center')
        head_format = workbook.add_format()
        head_format.set_align('center')
        head_format.set_bold()
        head_format.set_font_size(15)
        text_wrap = workbook.add_format()
        text_wrap.set_align('center')
        text_wrap.set_bold()
        text_wrap.set_bg_color('#c8cfc9')
        text_wrap.set_text_wrap()
        text_wrap.set_border()
        text_wrap1 = workbook.add_format()
        text_wrap1.set_align('center')
        text_wrap1.set_text_wrap()
        text_wrap1.set_border()
        text_wrap2 = workbook.add_format()
        text_wrap2.set_align('center')
        text_wrap2.set_text_wrap()
        text_wrap2.set_border()
        text_wrap2.set_bold()
        text_wrap3 = workbook.add_format()
        text_wrap3.set_align('left')
        text_wrap3.set_text_wrap()
        text_wrap3.set_border()
        text_wrap3.set_bold()
        text_wrap4 = workbook.add_format()
        text_wrap4.set_align('right')
        text_wrap4.set_bold()
        text_wrap4.set_bg_color('#c8cfc9')
        text_wrap4.set_text_wrap()
        text_wrap5 = workbook.add_format()
        text_wrap5.set_align('left')
        text_wrap5.set_bold()
        text_wrap5.set_bg_color('#c8cfc9')
        text_wrap5.set_text_wrap()

        bold1 = workbook.add_format()
        bold1.set_bold()
        bold1.set_align('center')
        bold1.set_text_wrap()
        bold2 = workbook.add_format()
        bold2.set_bold()
        bold2.set_bg_color('#89b3c9')
        bold3 = workbook.add_format()
        bold3.set_bold()
        bold3.set_align('center')
        bold3.set_font_size(18)
        bold3.set_bg_color('#f7f9fa')
        bold3.set_color('#8C2586')
        bold4 = workbook.add_format()
        bold4.set_bold()
        bold4.set_bg_color('#8497a1')
        bold4.set_align('left')
        bold5 = workbook.add_format()
        bold5.set_bold()
        bold5.set_bg_color('#8497a1')
        bold5.set_align('right')

        sheet = workbook.add_worksheet('Stock Ledger XLSX')
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 20)

        sheet.merge_range(0, 0, 1, 19, self.env.company.name, bold3)
        sheet.merge_range(2, 0, 3, 19, 'Stock Ledger', head_format)
        sheet.merge_range(4, 0, 5, 1, 'Location:', bold5)
        if data['warehouse']:
            sheet.merge_range(4, 2, 5, 3, data['warehouse'], bold4)
        else:
            sheet.merge_range(4, 2, 5, 3, 'All', bold4)
        sheet.merge_range(4, 4, 5, 5, 'Category:', bold5)
        if data['category']:
            sheet.merge_range(4, 6, 5, 7, data['category'], bold4)
        else:
            sheet.merge_range(4, 6, 5, 7, 'All', bold4)
        sheet.merge_range(4, 8, 5, 9, 'Color:', bold5)
        if data['color']:
            sheet.merge_range(4, 10, 5, 11, data['color'], bold4)
        else:
            sheet.merge_range(4, 10, 5, 11, 'All', bold4)
        sheet.merge_range(4, 12, 5, 13, 'Article:', bold5)
        if data['article']:
            sheet.merge_range(4, 14, 5, 15, data['article'], bold4)
        else:
            sheet.merge_range(4, 14, 5, 15, 'All', bold4)
        sheet.merge_range(4, 16, 5, 17, 'Inventory Date:', bold5)
        sheet.merge_range(4, 18, 5, 19, data['date'], bold4)
        col = 0
        sheet.merge_range(6, 0, 7, 0, 'Sr No.', text_wrap)
        col += 1
        sheet.merge_range(6, col, 7, col, 'Article', text_wrap)
        col += 1
        sheet.merge_range(6, col, 7, col, 'Color', text_wrap)
        col += 1
        for s in data['size']:
            sheet.merge_range(6, col, 7, col, s, text_wrap)
            col += 1
        sheet.merge_range(6, col, 7, col, 'Total Qty', text_wrap)

        row = 8
        sr = 0
        for lp in data['lis_pro']:
            sr = sr + 1
            col = 0
            sheet.write(row, col, sr, text_wrap1)
            sheet.write(row, col + 1, lp['article'], text_wrap1)
            for lc in lp['pro_name_color']:
                sheet.write(row, col + 2, lc['color_in_line'], text_wrap1)
                col_size = 3
                for lsc in lc['color_wise_size']:
                    sheet.write(row, col_size, lsc, text_wrap1)
                    col_size += 1
                sheet.write(row, col_size, lc['total_qty'], text_wrap1)
                row = row + 1
                sheet.write(row, col + 2, 'Total', text_wrap2)
                col_size = 3
                for sta in lp['sub_total_artical']:
                    sheet.write(row, col_size, sta, text_wrap2)
                    col_size += 1
                sheet.write(row, col_size, lp['sub_total_qty'], text_wrap2)
            row = row + 1
        row += 1
        sheet.merge_range(row, 0, row, 2, 'Grand Total', text_wrap3)
        col_size = 3
        if data['grand_total']:
            for gt in data['grand_total']:
                sheet.write(row, col_size, gt, text_wrap2)
                col_size += 1
        else:
            for gt in data['size']:
                sheet.write(row, col_size, 0, text_wrap2)
                col_size += 1
        sheet.write(row, col_size, data['grand_total_qty'], text_wrap2)
        sheet.merge_range(row + 2, 14, row + 2, 16, 'Generated By:', text_wrap4)
        sheet.merge_range(row + 2, 17, row + 2, 19, self.env.user.name, text_wrap5)
        sheet.merge_range(row + 3, 14, row + 3, 16, 'Printed on:', text_wrap4)
        sheet.merge_range(row + 3, 17, row + 3, 19, datetime.now().strftime("%Y/%m/%d %H:%M"),
                          text_wrap5)
