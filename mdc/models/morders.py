# -*- coding: utf-8 -*-

import datetime
from odoo import api, models, fields, _
from odoo.exceptions import UserError

class Lot(models.Model):
    """
    Main data for Lot (Manufacturing Orders Lots)
    """
    _name = 'mdc.lot'
    _description = 'Lot'

    name = fields.Char(
        'Name',
        required=True)
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True)
    weight =fields.Float(
        'Weight')
    w_uom_id = fields.Many2one(
        'product.uom',
        string = 'Weight Unit')
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer')
    descrip = fields.Char(
        'Description')


class LotActive(models.Model):
    """
    Main data for active lots
    """
    _name = 'mdc.lot_active'
    #_inherit = ['mdc.base.structure']
    _description = 'Active Lot'

    def _get_chkpoint_categ_selection(self):
        return [
            ('WIN', _('Input')),
            ('WOUT', _('Output')),
    ]


    lot_id = fields.Many2one(
        'mdc.lot',
        string='Lot',
        required=True)
    line_id = fields.Many2one(
        'mdc.line',
        string='Line',
        required=True)
    chkpoint_categ = fields.Selection(
        selection='_get_chkpoint_categ_selection',
        string='Checkpoint Categ',
        required=True)
    start_datetime = fields.Datetime(
        'Datetime_Start',
        required=True)
    end_datetime = fields.Datetime(
        'Datetime_End')
    total_hours = fields.Float(
        'Total hours',
        readonly=True,
        default=0,
        compute='_compute_total_hours')
    active = fields.Boolean(
        'Active',
        default=True)

    @api.depends('start_datetime', 'end_datetime')
    def _compute_total_hours(self):
        """
        Set the lot total hours
        :return:
        """
        for lot_active in self:
            total_hours = 0.0
            # TODO total_hours = end_datetime - start_datetime
            lot_active.update({
                'total_hours': total_hours
            })


class Worksheet(models.Model):
    """
    Main data for active lots
    """
    _name = 'mdc.worksheet'
    _description = 'Worksheet'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee')
    start_datetime = fields.Datetime(
        'Start Datetime',
        required=True,
        default = _default_date)
    end_datetime = fields.Datetime(
        'End Datetime')
    lot_id = fields.Many2one(
        'mdc.lot',
        string='Lot',
        required=True)
    workstation_id = fields.Many2one(
        'mdc.workstation',
        string='Workstation')
