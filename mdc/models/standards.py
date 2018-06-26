# -*- coding: utf-8 -*-

import datetime
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class Std(models.Model):
    """
    Main data for Lot (Manufacturing Orders Lots)
    """
    _name = 'mdc.std'
    _inherits = {'product.product': 'product_id'}
    _description = 'Standards'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='cascade')
    std_yield_product = fields.Float(
        'Std Yield Product')
    std_speed = fields.Float(
        'Std Speed')
    std_yield_sp1 = fields.Float(
        'Std Yield Subproduct 1')
    std_yield_sp2 = fields.Float(
        'Std Yield Subproduct 2')
    std_yield_sp3 = fields.Float(
        'Std Yield Subproduct 3')
