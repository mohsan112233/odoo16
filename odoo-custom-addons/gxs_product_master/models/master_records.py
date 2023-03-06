from odoo import models, fields, tools, api


class SeasonMaster(models.Model):
    _name = 'season.master'
    _description = 'Season'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')


class OriginMaster(models.Model):
    _name = 'origin.master'
    _description = 'Origin Master'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')


class TypeMaster(models.Model):
    _name = 'type.master'
    _description = 'Type Master'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')


class MarketMaster(models.Model):
    _name = 'market.master'
    _description = 'Market Master'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')


class BrandsMaster(models.Model):
    _name = 'brands.master'
    _description = 'Brands Master'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')


class MakeMaster(models.Model):
    _name = 'make.master'
    _description = 'Make Master'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')


class ArticalMarketCodeMaster(models.Model):
    _name = 'artical.market.code.master'
    _description = 'Artical / Market Code Master'

    name = fields.Char(string='Name')
    description = fields.Char(string='Description')


class ProductFieldsInherit(models.Model):
    _inherit = 'product.template'
    _description = 'Template Inherit'

    season_id = fields.Many2one('season.master', string='Season')
    origin_id = fields.Many2one('origin.master', string="Origin")
    type_id = fields.Many2one('type.master', string="Type")
    market_id = fields.Many2one('market.master', string="Market")
    brands_id = fields.Many2one('brands.master', string="Brands")
    make_id = fields.Many2one('make.master', string="Make")
    artical_market_code = fields.Many2one('artical.market.code.master', string="Artical / Market Code")
    cat_id = fields.Many2one(related='categ_id')
    raw = fields.Boolean(string="Raw Material")
    fg = fields.Boolean(string="Finished Good")

    @api.onchange('categ_id')
    def _onchange_category_id_in_products(self):
        a = self.env['product.category'].search([('id', '=', self.cat_id.id)])
        if not a.parent_id:
            if a.name == 'Raw Material':
                self.fg = False
                self.raw = True
                print('Succeed')
            else:
                self.fg = True
                self.raw = False
        elif a.parent_id:
            b = self.env['product.category'].search([('id', '=', a.parent_id.id)])
            if not b.parent_id:
                if b.name == 'Raw Material':
                    self.fg = False
                    self.raw = True
                    print('Succeed2')
                else:
                    self.fg = True
                    self.raw = False
            elif b.parent_id:
                c = self.env['product.category'].search([('id', '=', b.parent_id.id)])
                if not c.parent_id:
                    if c.name == 'Raw Material':
                        self.fg = False
                        self.raw = True
                        print('Succeed3')
                    else:
                        self.fg = True
                        self.raw = False
                elif c.parent_id:
                    d = self.env['product.category'].search([('id', '=', c.parent_id.id)])
                    if not d.parent_id:
                        if d.name == 'Raw Material':
                            self.fg = False
                            self.raw = True
                            print('Succeed4')
                        else:
                            self.fg = True
                            self.raw = False

        @api.constrains()
        def fg_raw():
            fg = self.fg
            raw = self.raw
            print(fg,raw)
            return fg,raw

        # elif b.parent_id:
        #     b = self.env['product.category'].search([('id', '=', b.cat_id.id)])
        #     if not b.parent_id:
        #         if b.name == 'Raw Material':
        #             print('Succeed')
