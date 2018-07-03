# -*- coding: utf-8 -*-

import logging
import datetime
from odoo import api, models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


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
    create_date = fields.Date(
        'Create_Date',
        required = True)
    end_date = fields.Date(
        'End_Date')


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
    chkpoint_id = fields.Many2one(
        'mdc.chkpoint',
        string='Checkpoint Id',
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

    @api.model
    def create(self, values):
        _logger.info("[SLV] LotActive create")
        # TODO: validar/cerrar el lote activo anterior del checkpoint seleccionado
        return super(LotActive, self).create(values)

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
