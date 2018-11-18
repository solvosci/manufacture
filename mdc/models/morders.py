# -*- coding: utf-8 -*-

import logging
import datetime
from odoo import api, models, fields, _, registry
from odoo.exceptions import UserError

from .. import ws_rfid_server
import websocket
import ast


_logger = logging.getLogger(__name__)


class Lot(models.Model):
    """
    Main data for Lot (Manufacturing Orders Lots)
    """
    _name = 'mdc.lot'
    _description = 'Lot'

    _sql_constraints = [
        ('lot_name_unique', 'UNIQUE(name)',
         _('The selected lot name already exists')),
    ]

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()
    def _default_uom(self):
        return self.env.ref('product.product_uom_kgm')

    name = fields.Char(
        'MO',
        required=True)
    product_id = fields.Many2one(
        'product.product',
        string='Product (Standard)',
        required=True)
    weight =fields.Float(
        'Weight',
        required=True)
    w_uom_id = fields.Many2one(
        'product.uom',
        string = 'Weight Unit',
        default=_default_uom)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer')
    lot_code= fields.Char(
        'Lot',
        required=True)
    descrip = fields.Text(
        'Observations')
    start_date = fields.Date(
        'Start Date',
        required=True,
        default=_default_date)
    end_date = fields.Date(
        'End_Date',
        required=True)
    std_loss = fields.Float(
        'Std Loss')
    std_yield_product = fields.Float(
        'Std Yield Product',
        digits=(10,3))
    std_speed = fields.Float(
        'Std Speed',
        digits=(10,3))
    std_yield_sp1 = fields.Float(
        'Std Yield Subproduct 1',
        digits=(10,3))
    std_yield_sp2 = fields.Float(
        'Std Yield Subproduct 2',
        digits=(10,3))
    std_yield_sp3 = fields.Float(
        'Std Yield Subproduct 3',
        digits=(10,3))
    total_gross_weight = fields.Float(
        'Real Total Gross Weight',
        readonly=True,
        default=0)
    alias_cp = fields.Char(
        'Alias CP name',
        compute='_compute_alias_cp',
    )

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
                prod_name= self.env['product.product'].browse(entry.product_id.id).name_get()[0][1]
                res.append((entry.id, '[%s (%s , %s)]: %s - (%s)' % (entry.name, entry.start_date, caduca, prod_name, cliente)))
        else:
            for entry in self:
                res.append((entry.id, '%s' % (entry.name)))
        return res

    def _lot_format(self, values):
        lotName = values['name']
        if lotName is None or lotName is False or lotName == '':
            return ''
        # lotPart2 must be current year (las 2 digits)
        currYear2 = str(datetime.datetime.now().year)[2:4]
        lotPart1 = '1'
        lotPart2 = currYear2
        lotRightFormat = True
        if lotName.find('/') > 0:
            lotPart1 = lotName[0:lotName.find('/')]
            lotPart2 = lotName[lotName.find('/')+1:len(lotName)]
        if lotName.find('/') == -1:
            lotPart1 = lotName
        if not lotPart1.isnumeric() or len(lotPart1) > 5:
            raise UserError(_('MO Format is not right. The right format is NNNNN/AA (NNNNN=number)'))
        if lotPart2 != currYear2:
            raise UserError(_('MO Format is not right. The right format is NNNNN/AA (AA=current year) %s != %s')
                              % (lotPart2, currYear2))

        return lotPart1.zfill(5)+'/'+lotPart2

    # compute total_gross_
    def compute_total_gross_weight(self, context):
        tot_gross_weight = 0
        woutlot = self.env['mdc.data_wout'].search([('lot_id', '=', context['lot_id'])])
        for wo in woutlot:
            tot_gross_weight += wo.gross_weight
        lot = self.browse(context['lot_id'])
        if lot:
            lot.total_gross_weight = tot_gross_weight

    @api.multi
    @api.depends('name', 'lot_code')
    def _compute_alias_cp(self):
        for lot in self:
            lot.alias_cp = '%s - %s' % (lot.name, lot.lot_code or '')

    @api.constrains('end_date')
    def _check_end_date(self):
        for l in self:
            if l.end_date < l.start_date:
                raise models.ValidationError(_('End date must be older than start date'))

    @api.onchange('name')
    def _retrieve_lot_format(self):
        for lot in self:
            lot.name = self._lot_format({'name': lot.name})

    @api.onchange('product_id')
    def _retrieve_std_data(self):
        for lot in self:
            std = self.env['mdc.std'].search([('product_id', '=', lot.product_id.id)])
            lot.std_loss = std.std_loss
            lot.std_yield_product = std.std_yield_product
            lot.std_speed = std.std_speed
            lot.std_yield_sp1 = std.std_yield_sp1
            lot.std_yield_sp2 = std.std_yield_sp2
            lot.std_yield_sp3 = std.std_yield_sp3

    @api.onchange('start_date')
    def _calculate_end_date(self):
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        default_life_days = int(IrConfigParameter.get_param('mdc.lot_default_life_days'))
        for lot in self:
            if lot.start_date is not None:
                w_start_date = fields.Datetime.from_string(lot.start_date)
                w_end_date = w_start_date + datetime.timedelta(days=default_life_days)
                lot.end_date = w_end_date.strftime("%Y-%m-%d %H:%M:%S")
            else:
                lot.end_date = None


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
        string='MO',
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
        if end_datetime is False:
            end_datetime = fields.Datetime.now()
        if start_datetime is not False and end_datetime is not False and start_datetime < end_datetime:
            difference = datetime.datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S') - datetime.datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
            total_hours = difference.days*24 + difference.seconds/3600
        return total_hours

    @api.constrains('start_datetime')
    def _check_start_datetime(self):
        for l in self:
            if not l.start_datetime and l.start_datetime > fields.Datetime.now():
                raise UserError(_('You can´t give a future start date'))
            id_lot_active = self.search(
                [('chkpoint_id', '=', l.chkpoint_id.id),
                 ('end_datetime', '>', l.start_datetime)])
            if id_lot_active:
                raise models.ValidationError(_('Start date must be older last end date'))

    @api.constrains('end_datetime')
    def _check_end_datetime(self):
        for l in self:
            if not l.end_datetime and l.end_datetime > fields.Datetime.now():
                raise UserError(_('You can´t give a future end date'))
            if l.end_datetime < l.start_datetime:
                raise models.ValidationError(_('End date must be older than start date'))

    @api.model
    def create(self, values):
        values['total_hours'] = self._compute_total_hours(values)
        return super(LotActive, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()

        if 'start_datetime' in values:
            print("write lot_active:  values['start_datetime'] " + values['start_datetime'] + " self.start_datetime: " + self.start_datetime)

        # update (if exists) historic lot with end_datetime the old start_date time
        if 'start_datetime' in values and values['start_datetime'] and self.start_datetime \
                and values['start_datetime'] != self.start_datetime:
            # validate that new and old start_datetime must be in the same shift
            shift_new = self.env['mdc.shift'].get_current_shift(values['start_datetime'])
            shift_old = self.env['mdc.shift'].get_current_shift(self.start_datetime)
            if shift_new['start_datetime'] != shift_old['start_datetime']:
                raise UserError(_('You can´t change start data to another date or shift'))
            # update (if exists) historic lot with end_datetime the old start_date time
            print("-> search change start_datetime: chkpoint_id: "+str(self.chkpoint_id.id)+", end_datetime: " + self.start_datetime)
            id_lot_search = self.search(
                [('chkpoint_id', '=', self.chkpoint_id.id), ('end_datetime', '=', self.start_datetime)])
            if not id_lot_search:
                # if we don´t find it at first, we search with active = False
                id_lot_search = self.search(
                    [('chkpoint_id', '=', self.chkpoint_id.id), ('end_datetime', '=', self.start_datetime), ('active', '=', False)])
            if id_lot_search:
                print("find id_lot_search change start_datetime: update end_datetime: from " + self.start_datetime + " to "+values['start_datetime'])
                id_lot_search.write({
                    'end_datetime': values['start_datetime'],
                    'total_hours': -1
                })
            else:
                print("-> search change start_datetime: don´t find")
            #if a checkpoint WOUT we have to refactoring the worksheet in this interval
            if self.chkpoint_id.chkpoint_categ == 'WOUT':
                start_change_interval = values['start_datetime']
                end_change_interval = self.start_datetime
                lot_active_interval = self.lot_id.id
                if 'lot_id' in values and not values['lot_id']:
                    lot_active_interval = values['lot_id'].id
                if self.start_datetime < values['start_datetime']:
                    start_change_interval = self.start_datetime
                    end_change_interval = values['start_datetime']
                    if id_lot_search:
                        lot_active_interval = id_lot_search.lot_id.id
                    else:
                        lot_active_interval = 0
                self.env['mdc.worksheet'].refactoring(
                    line_id=self.chkpoint_id.line_id,
                    shift_id=shift_new['shift'],
                    lot_active_interval=lot_active_interval,
                    start_change_interval=start_change_interval,
                    end_change_interval=end_change_interval)

        if 'end_datetime' in values:
            print("write lot_active:  values['end_datetime'] " + str(values['end_datetime']) + " self.end_datetime: " + str(self.end_datetime))

        # update (if exists) historic lot with start_datetime the old end_date time
        if 'end_datetime' in values and values['end_datetime'] and self.end_datetime \
                and values['end_datetime'] != self.end_datetime:
            fromModifStartDate = False
            #we know we went from update start_date because 'total_hours': -1
            if 'total_hours' in values and values['total_hours'] == -1:
                fromModifStartDate = True
            if not fromModifStartDate:
                print("-> search change end_datetime: chkpoint_id: " + str( self.chkpoint_id.id) + ", start_datetime: " + self.end_datetime)
                id_lot_search = self.search(
                    [('chkpoint_id', '=', self.chkpoint_id.id), ('start_datetime', '=', self.end_datetime)])
                if not id_lot_search:
                    # if we don´t find it at first, we search with active = False
                    id_lot_search = self.search(
                        [('chkpoint_id', '=', self.chkpoint_id.id), ('start_datetime', '=', self.end_datetime), ('active', '=', False)])
                if id_lot_search:
                    raise UserError(_( 'You can´t change this end datetime. You must change the start date of the active lot with start date this end date'))
                else:
                    print("-> search change end_datetime: don´t find")
                # validate that new and old end_datetime must be in the same shift
                shift_new = self.env['mdc.shift'].get_current_shift(values['end_datetime'])
                shift_old = self.env['mdc.shift'].get_current_shift(self.end_datetime)
                if shift_new['start_datetime'] != shift_old['start_datetime']:
                    raise UserError(_('You can´t change end data to another date or shift'))
                #if a checkpoint WOUT we have to refactoring the worksheet in this interval
                if self.chkpoint_id.chkpoint_categ == 'WOUT':
                    start_change_interval = values['end_datetime']
                    end_change_interval = self.end_datetime
                    if id_lot_search:
                        lot_active_interval = id_lot_search.lot_id.id
                    else:
                        lot_active_interval = 0
                    if self.end_datetime < values['end_datetime']:
                        start_change_interval = self.end_datetime
                        end_change_interval = values['end_datetime']
                        lot_active_interval = self.lot_id.id
                        if 'lot_id' in values and not values['lot_id']:
                            lot_active_interval = values['lot_id'].id
                    self.env['mdc.worksheet'].refactoring(
                        line_id=self.chkpoint_id.line_id,
                        shift_id=shift_new['shift'],
                        lot_active_interval=lot_active_interval,
                        start_change_interval=start_change_interval,
                        end_change_interval=end_change_interval)

        # compute total hours
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

    def update_start_date(self, chkpoint_id, new_start_lot_datetime, old_start_lot_datetime):
        # update (if exists) historic lot with start_datetime the old start_date time
        id_lot_search = self.search(
            [('chkpoint_id', '=', chkpoint_id), ('start_datetime', '=', old_start_lot_datetime)])
        if id_lot_search:
            print( "find update_start_date: " + str(id_lot_search.id) + " new_start_lot_datetime: " + new_start_lot_datetime)
            id_lot_search.write({
                'start_datetime': new_start_lot_datetime
            })
        #else:
        #    raise UserError(_('We can´t find '))

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

    def _online_update_total_hours(self):
        """
        Calculate total hours of lots without end date
        :return:
        """
        opened_lotActive = self.search([('end_datetime', '=', False)])
        if opened_lotActive:
            try:
                for lot in opened_lotActive:
                    # we execute write method without calculate total hours (we send zero)
                    # because in write method we calculate the real total_hours
                    lot.write({'total_hours': 0})
                    _logger.info('[mdc.lot_active] update_total_hours %s' % (lot.lot_id.name))
            except UserError as e:
                _logger.error('[mdc.lot_active] _online_update_total_hours:  %s' % e)
        """
        Calculate total hours of worksheet without end date
        :return:
        """
        opened_worksheet = self.env['mdc.worksheet'].search([('end_datetime', '=', False)])
        if opened_worksheet:
            try:
                for ws in opened_worksheet:
                    # we execute write method without calculate total hours (we send zero)
                    # because in write method we calculate the real total_hours
                    ws.write({'total_hours': 0})
                    _logger.info('[mdc.worksheet] update_total_hours %s - %s' % (ws.employee_id.name, ws.workstation_id.name))
            except UserError as e:
                _logger.error('[mdc.worksheet] _online_update_total_hours:  %s' % e)


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
        string='MO',
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

    @api.constrains('end_datetime')
    def _check_end_datetime(self):
        for l in self:
            if l.end_datetime is not False and l.start_datetime is not False \
                    and l.end_datetime < l.start_datetime:
                raise models.ValidationError(_('End date must be older than start date'))

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
        if end_datetime is False:
            end_datetime = fields.Datetime.now()
        if start_datetime is not False and end_datetime is not False and start_datetime < end_datetime:
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
        line_id = False
        em = self.env['hr.employee'].browse(values['employee_id'])
        if 'start_datetime' in values:
            # start_datetime must to be greater than last end_datetime
            if em.worksheet_end_datetime is not False and str(values['start_datetime']) < str(em.worksheet_end_datetime):
                raise UserError(_('It can´t be start datetime less than last end datetime to employee %s') % em.employee_code)
        else:
            # must be give a start date
            raise UserError(_('The start date has to be filled'))
        if 'end_datetime' in values:
            # end_datetime must to be greater than start_datetime
            if values['end_datetime'] is not False and str(values['end_datetime']) < str(values['start_datetime']):
                raise UserError(_('It can´t be end datetime less than start date to employee %s') % em.employee_code)
        if 'workstation_id' not in values:
            # get workstation pre-assigned data from employee (if the employee was pre-assigned to a workstation)
            (ws_id, shift_id, line_id) = self.env['mdc.workstation'].get_wosrkstation_data_by_employee(values['employee_id'])
            values['workstation_id'] = ws_id
            values['shift_id'] = shift_id
        else:
            # get shift and line for specific workstation
            if values['workstation_id']:
                ws = self.env['mdc.workstation'].browse(values['workstation_id'])
                line_id = ws.line_id.id
                values['shift_id'] = ws.shift_id.id
        # with line, get lot from chkpoint (WOUT chkpoint)
        if 'lot_id' not in values:
            if line_id:
                values['lot_id'] = self.env['mdc.chkpoint'].get_current_lot('WOUT', line_id)
        values['total_hours'] = self._compute_total_hours(values)
        return super(Worksheet, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()
        if 'employee_id' in values:
            if self.employee_id.id != values['employee_id']:
                raise UserError(_('You can´t change employee form a datasheet.'))
        if 'start_datetime' in values:
            #if self.start_datetime != values['start_datetime']:
            #    raise UserError(_('You can´t change start_datetime form a datasheet.'))
            # start_datetime must to be greater than last end_datetime
            if self.employee_id.worksheet_end_datetime is not False and str(values['start_datetime']) < str(self.employee_id.worksheet_end_datetime):
                raise UserError(_('It can´t be start datetime less than last end datetime to employee %s') % self.employee_id.employee_code)
        if 'end_datetime' in values:
            # end_datetime must to be greater than start_datetime
            if str(values['end_datetime']) < str(self.start_datetime):
                raise UserError(_('It can´t be end datetime less than start date to employee %s') % self.employee_id.employee_code)
        values['total_hours'] = self._compute_total_hours(values)
        return super(Worksheet, self).write(values)

    @api.multi
    def massive_close(self, wsheets, end_time):
        for item in wsheets:
            item.write({'end_datetime': end_time})
        return

    @api.multi
    def update_employee_worksheets(self, employee_id, new_workstation_id, now):
        # Look for employee open worksheets, and close them
        if not self.user_has_groups('mdc.group_mdc_office_worker'):
            raise UserError(_('You are not allowed to change this values'))
        wsheet = self.sudo().search(
            [('end_datetime', '=', False),
             ('employee_id', '=', employee_id)])
        self.sudo().massive_close(wsheet, now)
        # with new workstation create a new worksheet for this employee
        self.sudo().create({
            'start_datetime': now,
            'employee_id': employee_id,
            'workstation_id': new_workstation_id})
        return

    def refactoring(self, line_id, shift_id, lot_active_interval, start_change_interval, end_change_interval):
        print("refactoring: line_id: "+str(line_id)+", shift_id: "+str(shift_id)+", lot_active_interval: "+str(lot_active_interval)
              + ", start_change_interval: "+start_change_interval+", end_change_interval: "+end_change_interval+".")
        wsheet = self.search(
             ['|', '&', '&', '&', ('workstation_id.line_id', '=', line_id.id), ('shift_id', '=', shift_id.id),
                 ('end_datetime', '>=', start_change_interval), ('end_datetime', '<=', end_change_interval),
                 '&', '&', '&', ('workstation_id.line_id', '=', line_id.id), ('shift_id', '=', shift_id.id),
                 ('start_datetime', '>=', start_change_interval), ('start_datetime', '<=', end_change_interval)
             ], order='employee_id asc, start_datetime asc')
        numReg=0
        if wsheet:
            for ws in wsheet:
                numReg+=1
                print(str(numReg)+" find worksheet: ws.employee_id: " + str(ws.employee_id.id) +", ws.lot_id : " + str(ws.lot_id.id)
                      + ", ws.start_datetime: " + ws.start_datetime +", ws.end_datetime: " + str(ws.end_datetime) +".")
                if ws.start_datetime < start_change_interval:
                    if ws.lot_id.id != lot_active_interval:
                        updateEndDate = True
                        if ws.end_datetime and ws.end_datetime == start_change_interval:
                            updateEndDate = False
                        if updateEndDate:
                            rs_old_end_datetime = ws.end_datetime  # set in a temp variable de rs.end_datetime before update then
                            print("- write worksheet: ws.employee_id: " + str(ws.employee_id.id) + " update end_datetime: from "+ws.end_datetime+" to " +start_change_interval +".")
                            ws.write({'end_datetime': start_change_interval})
                            # if the next element has the same lot_id update the start_date of the next
                            ws2 = self.search([('employee_id', '=', ws.employee_id.id), ('start_datetime', '=', rs_old_end_datetime),
                                               ('workstation_id', '=', ws.workstation_id.id), ('shift_id', '=', ws.shift_id.id)])
                            updateStartDate = False
                            if ws2:
                                if not ws2.lot_id:
                                    if lot_active_interval == 0:
                                        updateStartDate = True
                                else:
                                    if lot_active_interval == ws2.lot_id.id:
                                        updateStartDate = True
                            if updateStartDate:
                                print("- write worksheet: ws.employee_id: " + str(ws.employee_id.id) + " start_datetime: from "+ws2.start_datetime +" to " + start_change_interval + ".")
                                ws2.write({'start_datetime': start_change_interval})
                            else:
                                print("- create worksheet: ws.employee_id: " + str(ws.employee_id.id) +", ws.lot_id : " + str(lot_active_interval)
                                        + ", ws.start_datetime: " + start_change_interval +", ws.end_datetime: " + str(ws.end_datetime) +".")
                                self.create({
                                    'employee_id': ws.employee_id.id,
                                    'start_datetime': start_change_interval,
                                    'end_datetime': rs_old_end_datetime,
                                    'lot_id': lot_active_interval,
                                    'workstation_id': ws.workstation_id.id,
                                    'shift_id': ws.shift_id.id})
                else:
                    if ws.lot_id.id != lot_active_interval:
                        if ws.end_datetime and ws.end_datetime <= end_change_interval:
                            print("* write worksheet: ws.employee_id: " + str(ws.employee_id.id) + ", start_datetime "+ws.start_datetime+", end_datetime "+ws.end_datetime
                                  + ", update lot_id: from "+str(ws.lot_id.id)+" to " + str(lot_active_interval) + ".")
                            ws.write({'lot_id': lot_active_interval})
                        else:
                            rs_old_start_datetime = ws.start_datetime  # set in a temp variable de rs.start_datetime before update then
                            print("* write worksheet: ws.employee_id: " + str(ws.employee_id.id) + ", update start_datetime: from "+ws.start_datetime+" to " + end_change_interval + ".")
                            ws.write({'start_datetime': end_change_interval})
                            # if the previous element has end_date = rs_old_start_datetime
                            ws2 = self.search(
                                [('employee_id', '=', ws.employee_id.id), ('end_datetime', '=', rs_old_start_datetime),
                                 ('workstation_id', '=', ws.workstation_id.id), ('shift_id', '=', ws.shift_id.id)])
                            if ws2:
                                # if exists previous element we have to update with end_date = rs_old_start_datetime
                                print("* write worksheet: ws.employee_id: " + str( ws.employee_id.id) + " update end_datetime: from " + ws2.end_datetime + " to " + end_change_interval + ".")
                                ws2.write({'end_datetime': end_change_interval})
                            else:
                                print("* create worksheet: ws.employee_id: " + str(ws.employee_id.id) + ", ws.lot_id : " + str(lot_active_interval)
                                      + ", ws.start_datetime: " + rs_old_start_datetime + ", ws.end_datetime: " + end_change_interval + ".")
                                self.create({
                                    'employee_id': ws.employee_id.id,
                                    'start_datetime': rs_old_start_datetime,
                                    'end_datetime': end_change_interval,
                                    'lot_id': lot_active_interval,
                                    'workstation_id': ws.workstation_id.id,
                                    'shift_id': ws.shift_id.id})
                            if ws.end_datetime and end_change_interval > ws.end_datetime:
                                print("* create worksheet: ws.employee_id: " +str(ws.employee_id.id) + ", ws.lot_id : " + str(lot_active_interval)
                                      + ", ws.start_datetime: " + ws.end_datetime + ", ws.end_datetime: " + end_change_interval + ".")
                                self.create({
                                    'employee_id': ws.employee_id.id,
                                    'start_datetime': ws.end_datetime,
                                    'end_datetime': end_change_interval,
                                    'lot_id': lot_active_interval,
                                    'workstation_id': ws.workstation_id.id,
                                    'shift_id': ws.shift_id.id})

        return

    @api.model
    def _listen(self):
        """
        Start listening open and close worksheet events through a websocket connection with RFID server
        :return:
        """
        _logger.info('[mdc.worksheet] Started listener')

        def process_card(card_code, card_datetime):
            # TODO since this process appears to execute in a single (and unique transaction),
            #      a new environment is needed
            # https://www.odoo.com/es_ES/forum/ayuda-1/question/how-to-get-a-new-cursor-on-new-api-on-thread-63441
            with api.Environment.manage():
                with registry(self.env.cr.dbname).cursor() as new_cr:
                    # Create a new environment with new cursor database
                    new_env = api.Environment(new_cr, self.env.uid, self.env.context)

                    ###############################################################################################
                    card = new_env['mdc.card'].search([('name', '=', card_code)])
                    try:
                        if card:
                            if card.employee_id:
                                if card.employee_id.present:
                                    card.employee_id.worksheet_close(card_datetime)
                                    _logger.info(
                                        '[mdc.worksheet] Made close worksheet action for employee with code %s' %
                                        card.employee_id.employee_code)
                                else:
                                    card.employee_id.worksheet_open(card_datetime)
                                    _logger.info(
                                        '[mdc.worksheet] Made open worksheet action for employee with code %s' %
                                        card.employee_id.employee_code)
                            else:
                                raise UserError(_('Card #%s is not an employee one') % card_code)
                        else:
                            raise UserError(_('Unknown card code #%s') % card_code)

                    except UserError as e:
                        _logger.error('[mdc.worksheet] Processing card: %s', e)
                    ###############################################################################################

                    new_env.cr.commit()  # Don't show a invalid-commit in this case
                # You don't need close your cr because is closed when finish "with"
            # You don't need clear caches because is cleared when finish "with"

        def on_message(ws, message):
            """
            ['Event']['user_id']['user_id']  <== card id.
            ['Event']['device_id']['id']  <== device id
            """
            _logger.info('[mdc.worksheet] Received: %s' % message)
            event = ast.literal_eval(message)
            # TODO verify proper event format (e.g. open websocket event is different)
            _logger.info('[mdc.worksheet] Read %s card from %s device!!!' %
                         (event['Event']['user_id']['user_id'], event['Event']['device_id']['id']))
            process_card(event['Event']['user_id']['user_id'], fields.Datetime.now())


        def on_error(ws, error):
            _logger.info('[mdc.worksheet] Websocket error: %s' % error)
            # TODO reconnect? Finish monitoring?

        def on_close(ws):
            _logger.info('[mdc.worksheet] Websocket closed!')

        def on_open(ws):
            _logger.info('[mdc.worksheet] Websocket open')
            ws.send('bs-session-id=%s' % ws_session_data['session_id'])
            _logger.info('[mdc.worksheet] Websocket session id sent')

        # TODO manage server errors and notice them
        ws_session_data = ws_rfid_server.get_session_data(self.env)
        # websocket.enableTrace(True)
        ws_server = websocket.WebSocketApp(ws_session_data['wsapi_url'],
                                           on_message=on_message,
                                           on_error=on_error,
                                           on_close=on_close)
        ws_server.on_open = on_open
        ws_server.run_forever()

        # Only when websocket is closed will end listener. Then, cron job should restart as soon as possible
        _logger.info('[mdc.worksheet] Ended listener')

