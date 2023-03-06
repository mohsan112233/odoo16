from odoo import models, fields, api


class SaleViewInherit(models.Model):
    _inherit = 'product.product'


    qty_available = fields.Float(
        'Quantity On Hand', compute='_compute_quantities', store=True, search='_search_qty_available',
        digits='Product Unit of Measure', compute_sudo=False,
        help="Current quantity of products.\n"
             "In a context with a single Stock Location, this includes "
             "goods stored at this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "stored in the Stock Location of the Warehouse of this Shop, "
             "or any of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")
    virtual_available = fields.Float(
        'Forecasted Quantity', compute='_compute_quantities', store=True, search='_search_virtual_available',
        digits='Product Unit of Measure', compute_sudo=False,
        help="Forecast quantity (computed as Quantity On Hand "
             "- Outgoing + Incoming)\n"
             "In a context with a single Stock Location, this includes "
             "goods stored in this location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")
    free_qty = fields.Float(
        'Free To Use Quantity ', compute='_compute_quantities', search='_search_free_qty',
        digits='Product Unit of Measure', compute_sudo=False, store=True,
        help="Forecast quantity (computed as Quantity On Hand "
             "- reserved quantity)\n"
             "In a context with a single Stock Location, this includes "
             "goods stored in this location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods stored in the Stock Location of this Warehouse, or any "
             "of its children.\n"
             "Otherwise, this includes goods stored in any Stock Location "
             "with 'internal' type.")
    incoming_qty = fields.Float(
        'Incoming', compute='_compute_quantities', search='_search_incoming_qty',
        digits='Product Unit of Measure', compute_sudo=False, store=True,
        help="Quantity of planned incoming products.\n"
             "In a context with a single Stock Location, this includes "
             "goods arriving to this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods arriving to the Stock Location of this Warehouse, or "
             "any of its children.\n"
             "Otherwise, this includes goods arriving to any Stock "
             "Location with 'internal' type.")
    outgoing_qty = fields.Float(
        'Outgoing', compute='_compute_quantities', search='_search_outgoing_qty',
        digits='Product Unit of Measure', compute_sudo=False, store=True,
        help="Quantity of planned outgoing products.\n"
             "In a context with a single Stock Location, this includes "
             "goods leaving this Location, or any of its children.\n"
             "In a context with a single Warehouse, this includes "
             "goods leaving the Stock Location of this Warehouse, or "
             "any of its children.\n"
             "Otherwise, this includes goods leaving any Stock "
             "Location with 'internal' type.")

    # nbr_moves_in = fields.Integer(compute='_compute_nbr_moves', compute_sudo=False, store=True,
    #                               help="Number of incoming stock moves in the past 12 months")
    # nbr_moves_out = fields.Integer(compute='_compute_nbr_moves', compute_sudo=False,
    #                                help="Number of outgoing stock moves in the past 12 months")
    nbr_reordering_rules = fields.Integer('Reordering Rules', store=True,
                                          compute='_compute_nbr_reordering_rules', compute_sudo=False)
    # reordering_min_qty = fields.Float(
    #     compute='_compute_nbr_reordering_rules', store=True, compute_sudo=False)
    # reordering_max_qty = fields.Float(
    #     compute='_compute_nbr_reordering_rules', store=True, compute_sudo=False)

    standard_price = fields.Float(
        'Product Cost', company_dependent=True,
        store=True,
        readonly=True,
        digits='Product Price',
        help="""In Standard Price & AVCO: value of the product (automatically computed in AVCO).
        In FIFO: value of the next unit that will leave the stock (automatically computed).
        Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
        Used to compute margins on sale orders.""")
    lst_price = fields.Float(
        'Sales Price', compute='_compute_product_lst_price',
        digits='Product Price', inverse='_set_product_lst_price', store=True,
        help="The sale price is managed from the product template. Click on the 'Configure Variants' button to set the extra attribute prices.")
