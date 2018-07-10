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

    def name_get(self, context=None):
        if context is None:
            context = {}
        res = []
        # FIXME it Doesn't Work - it always goes inside the if lines
        if context.get('name_extended', True):
            # Only one context possible
            for entry in self:
                if not entry.partner_id.name:
                    cliente = ''
                else:
                    cliente = entry.partner_id.name
                if not entry.end_date:
                    caduca = ''
                else:
                    caduca = entry.end_date
                res.append((entry.id, '[%s (%s , %s)]: %s - (%s)' % (entry.name, entry.create_date, caduca, entry.product_id.name, cliente)))
        else:
            for entry in self:
                res.append((entry.id, '%s' % (entry.name)))
        return res

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

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

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
        required=True,
        default=_default_date)
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

    @api.multi
    def write(self, values):
        self.ensure_one()
        # TODO actualizar total_hours de lot_employee
        return super(LotActive, self).write(values)

class Worksheet(models.Model):
    """
    Detailled employee time
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

    @api.model
    def create(self, values):
        _logger.info("[SLV] Worksheet create")
        # TODO actualizar total_hours de lot_employee
        return super(Worksheet, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()
        # TODO actualizar total_hours de lot_employee
        return super(Worksheet, self).write(values)


class LotEmployee(models.Model):
    """
    Employee time grouped by lot
    """
    _name = 'mdc.lot_employee'
    _description = 'Lot Employee Data'

    lot_id = fields.Many2one(
        'mdc.lot',
        string='Lot',
        required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True)
    work_date = fields.Date(
        string='Work Date',
        required=True)
    shift_id = fields.Many2one(
        'mdc.shift',
        string='Shift',
        required=True)
    total_hours = fields.Float(
        'Total Hours',
        required=True)
