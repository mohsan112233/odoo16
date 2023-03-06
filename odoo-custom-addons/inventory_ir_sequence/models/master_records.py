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
    raw = fields.Boolean(string="Raw Material", default=False)
    fg = fields.Boolean(string="Finished Good", deffault=False)
    val = fields.Char(string="Values")

    @api.onchange('categ_id')
    def _onchange_category_id_in_products(self):
        self.fg = False
        self.raw = False
        a = self.env['product.category'].search([('id', '=', self.cat_id.id)])
        if not a.parent_id:
            if a.name[:2] == 'RM':
                self.fg = False
                self.raw = True
            elif a.name[:2] == 'FG':
                self.fg = True
                self.raw = False

        elif a.parent_id:
            b = self.env['product.category'].search([('id', '=', a.parent_id.id)])
            if not b.parent_id:
                if b.name[:2] == 'RM':
                    self.fg = False
                    self.raw = True
                elif b.name[:2] == 'FG':
                    self.fg = True
                    self.raw = False

            elif b.parent_id:
                c = self.env['product.category'].search([('id', '=', b.parent_id.id)])
                if not c.parent_id:
                    if c.name[:2] == 'RM':
                        self.fg = False
                        self.raw = True
                    elif c.name[:2] == 'FG':
                        self.fg = True
                        self.raw = False

                elif c.parent_id:
                    d = self.env['product.category'].search([('id', '=', c.parent_id.id)])
                    if not d.parent_id:
                        if d.name[:2] == 'RM':
                            self.fg = False
                            self.raw = True
                        elif d.name[:2] == 'FG':
                            self.fg = True
                            self.raw = False

                else:
                    self.fg = False
                    self.raw = False
            else:
                self.fg = False
                self.raw = False
        else:
            self.fg = False
            self.raw = False

    @api.constrains('fg', 'raw')
    def fg_raw_codes_concatenate(self):
        if self.fg == True and self.raw == False:
            self.val = self.season_id.description + '-' + self.origin_id.description + '-' + self.type_id.description + '-' \
                       + self.market_id.description + '-' + self.brands_id.description
            print(self.val)
            strs = ''

            return self.val
        if self.fg == False and self.raw == True:
            self.val = self.make_id.description + '-' + self.artical_market_code.description
            print(self.val)
            return self.val
        # elif b.parent_id:
        #     b = self.env['product.category'].search([('id', '=', b.cat_id.id)])
        #     if not b.parent_id:
        #         if b.name == 'Raw Material':
        #             print('Succeed')
