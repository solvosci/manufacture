# -*- coding: utf-8 -*-

import datetime
from odoo import api, models, fields, _
from odoo.exceptions import UserError

class DataWIn(models.Model):
    """
    Main data for a chkpoint_datacapture weight input
    """
    _name = 'slv.mdc.data_w_in'
    _description = 'Weight Input Data'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    line_id = fields.Many2one(
        'slv.mdc.line',
        string='Line',
        required=True)
    lot_id = fields.Many2one(
        'slv.mdc.lot',
        string='Lot',
        required=True)
    create_datetime = fields.Datetime(
        'Datetime',
        required=True,
        default=_default_date)
    tare = fields.Float(
        'Tare',
        required=True)
    weight = fields.Float(
        'Weight',
        default=0)
    w_uom_id = fields.Many2one(
        'product.uom',
        string='Weight_uom')
    card_id = fields.Many2many(
        'slv.mdc.card',
        string='Card')
    w_out_id = fields.Many2one(
        'slv.mdc.data_w_out',
        string='W_Out')


class DataWOut(models.Model):
    """
    Main data for a chkpoint_datacapture weight input
    """
    _name = 'slv.mdc.data_w_out'
    _description = 'Weight Output Data'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    line_id = fields.Many2one(
        'slv.mdc.line',
        string='Line',
        required=True)
    lot_id = fields.Many2one(
        'slv.mdc.lot',
        string='Lot',
        required=True)
    create_datetime = fields.Datetime(
        'Datetime',
        required=True,
        default=_default_date)
    tare = fields.Float(
        'Tare',
        required=True)
    weight = fields.Float(
        'Weight',
        default=0)
    w_uom_id = fields.Many2one(
        'product.uom',
        string='Weight_uom')
    quality_id = fields.Many2one(
        'slv.mdc.quality',
        string='Quality')
    card_ids = fields.Many2many(
        'slv.mdc.card',
        string='Card')
    workstation_id = fields.Many2one(
        'slv.mdc.workstation',
        string='Workstation')
    shift_id = fields.Many2one(
        'slv.mdc.shift',
        string='Shift',
        required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee')
    shared = fields.Boolean(
        string='Shared',
        default=False)
    w_out_shared_id =fields.Many2one(
        'slv.mdc.data_w_out',
        string='Shared with')
    w_out_categ_id = fields.Many2one(
        'slv.mdc.w_out_categ',
        string='Out Category')
    gross_weight = fields.Float(
        'Gross Weight',
        readonly=True,
        default=0,
        compute='_compute_gross_weight')

    @api.depends('weight')
    def _compute_gross_weight(self):
        """
        Set gross weight
        :return:
        """
        for data_w_out in self:
            gross_weight = 0.0
            # TODO
            data_w_out.update({
                'gross_weight': gross_weight
            })