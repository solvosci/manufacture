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
        default=0)
    active = fields.Boolean(
        'Active',
        default=True)

    def _compute_total_hours(self, values):
        total_hours = 0.0
        start_datetime = self.start_datetime
        if 'start_datetime' in values:
            start_datetime = values['start_datetime']
        end_datetime = self.end_datetime
        if 'end_datetime' in values:
            end_datetime = values['end_datetime']
        if start_datetime is not False and end_datetime is not False:
            diference = datetime.datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
            total_hours = diference.days*24 + diference.seconds/3600

        return total_hours

    @api.model
    def create(self, values):
        values['total_hours'] = self._compute_total_hours(values)
        return super(LotActive, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()
        values['total_hours'] = self._compute_total_hours(values)
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
    shift_id = fields.Many2one(
        'mdc.shift',
        string='Shift',
        readonly=True)
    total_hours = fields.Float(
        'Total hours',
        readonly=True,
        default=0)

    def _retrieve_shift(self, values):
        shift = False
        workstation_id = self.workstation_id
        if 'workstation_id' in values:
            workstation_id = values['workstation_id']
        if workstation_id is not False:
            workstation = self.env['mdc.workstation'].browse(workstation_id.id)
            if workstation:
                shift =  workstation.shift_id.id
        return shift

    @api.onchange('workstation_id')
    def _retrieve_workstation_data(self):

        for worksheet in self:
            # search shift of workstation
            if worksheet.workstation_id:
                worksheet.shift_id = worksheet.workstation_id.shift_id

    def _compute_total_hours(self, values):
        total_hours = 0
        start_datetime = self.start_datetime
        if 'start_datetime' in values:
            start_datetime = values['start_datetime']
        end_datetime = self.end_datetime
        if 'end_datetime' in values:
            end_datetime = values['end_datetime']
        if start_datetime is not False and end_datetime is not False:
            end_date = datetime.datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
            start_date = datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
            timedelta = end_date - start_date
            total_hours = timedelta.seconds / 3600

        return total_hours

    @api.onchange('start_datetime', 'end_datetime')
    def _retrieve_total_hours(self):

        for worksheet in self:
            # compute total_hours
            total_hours = 0
            if worksheet.start_datetime is not False and worksheet.end_datetime is not False:
                end_datetime = datetime.datetime.strptime(worksheet.end_datetime, '%Y-%m-%d %H:%M:%S')
                start_datetime = datetime.datetime.strptime(worksheet.start_datetime, '%Y-%m-%d %H:%M:%S')
                timedelta = end_datetime - start_datetime
                total_hours = timedelta.seconds / 3600
            worksheet.total_hours = total_hours

    @api.model
    def create(self, values):
        values['shift_id'] = self._retrieve_shift(values)
        values['total_hours'] = self._compute_total_hours(values)
        return super(Worksheet, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()
        values['shift_id'] = self._retrieve_shift(values)
        values['total_hours'] = self._compute_total_hours(values)
        return super(Worksheet, self).write(values)