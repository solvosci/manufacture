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


    def update_historical(self, chkpoint_id, current_lot_active, new_lot_active_id, start_lot_datetime):
        # Modifying a current_lot_active
        if (current_lot_active) and (current_lot_active.id != new_lot_active_id):
            # In this case, Close historic lot_active
            id_lot_active = self.search(
                [('lot_id', '=', current_lot_active.id), ('chkpoint_id', '=', chkpoint_id), ('end_datetime', '=', False)])
            if id_lot_active:
                id_lot_active.write({
                    'end_datetime': start_lot_datetime,
                    'active': False,
                })
        if (new_lot_active_id) and (current_lot_active.id != new_lot_active_id):
            # In this case, Open new historic lot_active
            self.create({
                'lot_id': new_lot_active_id,
                'chkpoint_id': chkpoint_id,
                'start_datetime': start_lot_datetime
            })
        return


    def update_historical_old(self, values, chkpoint_id, lot_active):
        # Modifying a current_lot_active
        start_lot_datetime = fields.Datetime.now()
        new_lot_active = lot_active
        if 'current_lot_active_id' in values:
            new_lot_active = values.get('current_lot_active_id')
        if (lot_active != new_lot_active) and (lot_active):
            # In this case, Close historic lot_active
            id_lot_active = self.search(
                [('lot_id', '=', lot_active), ('chkpoint_id', '=', chkpoint_id), ('end_datetime', '=', False)])
            if id_lot_active:
                id_lot_active.write({
                    'end_datetime': start_lot_datetime,
                    'active': False,
                })
        if (lot_active != new_lot_active) and new_lot_active and (new_lot_active is not None):
            # In this case, Open new historic lot_active
            self.create({
                'lot_id': new_lot_active,
                'chkpoint_id': chkpoint_id,
                'start_datetime': start_lot_datetime
            })
        values['start_lot_datetime'] = start_lot_datetime
        return


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
        string='Employee',
        required = True)
    start_datetime = fields.Datetime(
        'Start Datetime',
        required=True,
        default = _default_date)
    end_datetime = fields.Datetime(
        'End Datetime')
    lot_id = fields.Many2one(
        'mdc.lot',
        string='Lot',
        readonly=True)
    workstation_id = fields.Many2one(
        'mdc.workstation',
        string='Workstation',
        readonly=True)
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
        # get workstation from employee
        # If workstation, get shift and line from workstation assigned to the employee
        (ws, shift, line) = self.env['mdc.workstation'].get_wosrkstation_assign_data(values['employee_id'])
        values['workstation_id'] = ws
        values['shift_id'] = shift
        # with line, get lot from chkpoint (WOUT chkpoint)
        if 'lot_id' not in values:
            values['lot_id'] = self.env['mdc.chkpoint'].get_current_lot('WOUT', line)
        values['total_hours'] = self._compute_total_hours(values)
        return super(Worksheet, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()
        if 'employee_id' in values:
            if self.employee_id.id != values['employee_id']:
                raise UserError(_('You can´t change employee form a datasheet.'))
        if 'start_datetime' in values:
            if self.start_datetime != values['start_datetime']:
                raise UserError(_('You can´t change start_datetime form a datasheet.'))
        values['total_hours'] = self._compute_total_hours(values)
        return super(Worksheet, self).write(values)

    @api.multi
    def massive_close(self, wsheets, end_time):
        for item in wsheets:
            item.write({'end_datetime': end_time})
        return