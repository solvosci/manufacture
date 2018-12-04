# -*- coding: utf-8 -*-

import datetime
import logging
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class BaseStructure(models.AbstractModel):
    """
    Allocates common functionality for Structure modules
    """
    _name = 'mdc.base.structure'
    _description = 'Base Structure model'

    def _get_chkpoint_categ_selection(self):
        return [
            ('WIN', _('Input')),
            ('WOUT', _('Output')),
    ]

    def _get_card_status_selection(self):
        return [
            ('USE', _('In Use')),
            ('IDLE', _('Idle')),
            ('BLOCKED', _('Blocked'))
    ]
    

class Line(models.Model):
    """
    Main data for a line
    """
    _name = 'mdc.line'
    _description = 'Line'

    _sql_constraints = [
        ('line_code_unique', 'UNIQUE(line_code)',
         _('Line_Code has been already assigned to a Line!')),
    ]

    name = fields.Char(
        'Name',
        required=True)
    line_code = fields.Char(
        'Line Code',
        required=True)


class ChkPoint(models.Model):
    """
    Main data for a chkpoint (check points)
    """
    _name = 'mdc.chkpoint'
    _inherit = ['mdc.base.structure']
    _description = 'Check Point'

    _sql_constraints = [
        ('line_chkpoint_categ_unique', 'UNIQUE(chkpoint_categ,line_id)',
         _('Combination: Line & Checkpoint category, are unique, and already Exists!')),
        ('allowed_ip_unique', 'UNIQUE(allowed_ip)',
         _('The selected allowed IP is already assigned!')),
    ]

    name = fields.Char(
        'Name',
        required=True)
    chkpoint_categ = fields.Selection(
        selection='_get_chkpoint_categ_selection',
        string='Checkpoint Category')
    line_id = fields.Many2one(
        'mdc.line',
        string='Line',
        required=True)
    order =fields.Integer(
        'order',
        required=True)
    scale_id = fields.Many2one(
        'mdc.scale',
        string='Scale')
    rfid_reader_id = fields.Many2one(
        'mdc.rfid_reader',
        string='RFID Reader')
    tare_id = fields.Many2one(
        'mdc.tare',
        string='Tare')
    quality_id = fields.Many2one(
        'mdc.quality',
        string='Quality')
    current_lot_active_id = fields.Many2one(
        'mdc.lot',
        string='Current MO Active Id')
    start_lot_datetime = fields.Datetime(
        string = 'Start MO Active date time'
        )
    allowed_ip = fields.Char(
        'Allowed IP'
    )

    @api.multi
    def write(self, values):
        self.ensure_one()
        now = fields.Datetime.now()

        # save new lot on a temp variable
        new_lot_active_id = 0
        if 'current_lot_active_id' in values:
            new_lot_active_id = values['current_lot_active_id']
        else:
            new_lot_active_id = self.current_lot_active_id.id

        # save new and old start-date on a temp variables
        new_start_lot_datetime = ''
        old_start_lot_datetime = ''
        if 'start_lot_datetime' in values:
            # default date = current_date
            if not values['start_lot_datetime']:
                values['start_lot_datetime'] = now
            # when change lot and don´t change date we put default date = current_date
            if 'current_lot_active_id' in values \
                and values['current_lot_active_id'] != self.current_lot_active_id.id \
                and values['start_lot_datetime'] == self.start_lot_datetime:
                values['start_lot_datetime'] = now
            new_start_lot_datetime = values['start_lot_datetime']
            old_start_lot_datetime = self.start_lot_datetime

        if new_start_lot_datetime:
            if new_start_lot_datetime > now:
                raise UserError(_('You can´t give a future start date'))

        #when change lot whe have to do new history records
        # Modifying a current_lot_active and update historic lot_active if it is necessary
        if 'current_lot_active_id' in values and values['current_lot_active_id'] != self.current_lot_active_id.id:
            _logger.info("Change lot: new : %s old: %s"
                         % (values['current_lot_active_id'], self.current_lot_active_id.id))
            if not new_start_lot_datetime:
                new_start_lot_datetime = now
            values['start_lot_datetime'] = new_start_lot_datetime
            # when change lot maybe do in the current shift
            shift_data = self.env['mdc.shift'].get_current_shift(now)
            if self.chkpoint_categ == 'WOUT':
                if new_start_lot_datetime < shift_data['start_datetime']:
                    raise UserError(_('You can´t give start date less than start current shift time (%s < %s)') % (new_start_lot_datetime, shift_data['start_datetime']))
                if new_start_lot_datetime > shift_data['end_datetime']:
                    raise UserError(_('You can´t give start date higher than end current shift time (%s > %s)') % (new_start_lot_datetime, shift_data['end_datetime']))

            old_start_lot_datetime = values['start_lot_datetime']
            self.env['mdc.lot_active'].update_historical(
                chkpoint_id=self.id,
                line_id=self.line_id,
                shift_id=shift_data['shift'],
                current_lot_active=self.current_lot_active_id,
                new_lot_active_id=values['current_lot_active_id'],
                start_lot_datetime=values['start_lot_datetime'])

        # if change start data we have do refactoring history of the lot
        if new_start_lot_datetime and old_start_lot_datetime \
                and new_start_lot_datetime != old_start_lot_datetime:
            _logger.info("change start_lot_datetime : new: %s old: %s"
                         % (new_start_lot_datetime, old_start_lot_datetime))
            self.env['mdc.lot_active'].update_start_date(
                chkpoint_id=self.id,
                new_lot_active_id=new_lot_active_id,
                new_start_lot_datetime=new_start_lot_datetime,
                old_start_lot_datetime=old_start_lot_datetime)

        return super(ChkPoint, self).write(values)


    @api.model
    def get_current_lot(self, chkpoint_categ, line_id):
        lot = self.search([('chkpoint_categ', '=', chkpoint_categ),('line_id', '=', line_id)])
        return lot.current_lot_active_id.id

class Workstation(models.Model):
    """
    Main data for a workstation
    """
    _name = 'mdc.workstation'
    _inherit = ['mdc.base.structure']
    _description = 'Workstation'

    _sql_constraints = [
        ('current_employee_unique', 'UNIQUE(current_employee_id)',
         _('The employee has been already assigned to a workstation!')),
        ('workstation_unique', 'UNIQUE(line_id, shift_id, seat)',
         _("There's already a workstation with the same line, shift and seat values")),
    ]

    name = fields.Char(
        'Workstation',
        required=True)
    line_id = fields.Many2one(
        'mdc.line',
        string='Line',
        required=True)
    shift_id = fields.Many2one(
        'mdc.shift',
        string='Shift',
        required=True)
    seat = fields.Char(
        'Seat',
        required=True)
    current_employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        index=True,
        ondelete='cascade',
        domain=[('workstation_id', '=', False)])
    last_wout_lot_id = fields.Many2one(
        'mdc.lot',
        string='Last output lot processed',
        compute='_compute_last_wout_lot'
    )

    def _compute_last_wout_lot(self):
        """
        Computes the last output used lot by a certain workstation
        :return:
        """
        Wout = self.env['mdc.data_wout'].sudo()
        for workstation in self:
            workstation_last_wout = Wout.search([('workstation_id', '=', workstation.id)],
                                                order='create_datetime desc', limit=1)
            if workstation_last_wout:
                workstation.last_wout_lot_id = workstation_last_wout.lot_id

    def massive_deallocate(self):
        workstation_sel = self.browse(self._context['active_ids'])
        if workstation_sel:
            for wk in workstation_sel:
                wk.write({
                    'current_employee_id': False
                })

    @api.model
    def get_wosrkstation_data_by_employee(self, employee_id):
        ws = self.search([('current_employee_id', '=', employee_id)])
        if ws:
            return (ws.id, ws.shift_id.id, ws.line_id.id)
        return (False,False,False)

    @api.multi
    def write(self, values):
        self.ensure_one()
        # Modify worksheets for employee changes
        if 'current_employee_id' in values:
            now = fields.Datetime.now()
            new_employee = self.env['hr.employee'].browse(values['current_employee_id'])
            if new_employee.id != self.current_employee_id.id:
                if self.current_employee_id.present:
                    # close worksheet for old employee and create new worksheet without workstation assign
                    self.env['mdc.worksheet'].update_employee_worksheets(self.current_employee_id.id, False, now)
                if new_employee.present:
                    # close worksheet for new employeeCreate worksheet for new employee assigned
                    self.env['mdc.worksheet'].update_employee_worksheets(new_employee.id, self.id, now)
        return super(Workstation, self).write(values)


class Card(models.Model):
    """
    Main data for a cards
    """
    _name = 'mdc.card'
    _inherit = ['mdc.base.structure']
    _description = 'Card'
    _order = 'name'

    _sql_constraints = [
        ('card_name_unique', 'UNIQUE(name)', _("There's another card with the same code")),
    ]

    name = fields.Integer(
        'Card_Code',
        required=True)
    card_categ_id = fields.Many2one(
        'mdc.card_categ',
        string='Card_Categ',
        required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        domain=[('operator', '=', True)])
    workstation_id = fields.Many2one(
        'mdc.workstation',
        string='Workstation')
    lot_id = fields.Many2one(
        'mdc.lot',
        string='Associated MO')
    status = fields.Selection(
        selection='_get_card_status_selection',
        string='Status')
    active = fields.Boolean(
        'Active',
        default=True)

    @api.model
    def create(self, values):
        values = self._card_preprocess(values)
        return super(Card, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()
        if 'card_categ_id' in values:
            raise UserError(_('Modifying card category is not allowed. Please contact Administrator'))
        if self.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_O').id:
            if 'employee_id' in values and not values.get('employee_id'):
                raise UserError(_('You must select an employee for this card'))
            values.pop('lot_id', None)
            values.pop('workstation_id', None)
        if self.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_L').id:
            if 'workstation_id' in values and not values.get('workstation_id'):
                raise UserError(_('You must select a workstation for this card'))
            values.pop('lot_id', None)
            values.pop('employee_id', None)
        if self.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_PC').id:
            # TODO for joker cards, if lot becomes required uncomment the code below
            """
            if 'lot_id' in values and not values.get('lot_id'):
                raise UserError(_('You must select a lot for this card'))
            """
            values.pop('employee_id', None)
            values.pop('workstation_id', None)
        # TODO product and subproduct cards should clear assignment fields
        return super(Card, self).write(values)

    # TODO modify _card_preprocess() for update validation
    def _card_preprocess(self, values):
        categ = values.get('card_categ_id')
        if categ == self.env.ref('mdc.mdc_card_categ_O').id:
            if not values.get('employee_id'):
                raise UserError(_('You must select an employee for this card or select another category'))
            values.pop('workstation_id', None)
            values.pop('lot_id', None)
        if categ == self.env.ref('mdc.mdc_card_categ_L').id:
            if not values.get('workstation_id'):
                raise UserError(_('You must select a workstation for this card or select another category'))
            values.pop('employee_id', None)
            values.pop('lot_id', None)
        if categ == self.env.ref('mdc.mdc_card_categ_PC').id:
            """
            # TODO from mdc controller interface it's possible to register a joker card without initial lot assignment
            if not values.get('lot_id'):
                raise UserError(_('You must select a lot for this card or select another category'))
            """
            values.pop('employee_id', None)
            values.pop('workstation_id', None)
        # TODO product and subproduct cards should clear assignment fields
        return values

    def from_cp_get_card_data(self, card_code):
        """
        Retrieves relevant data from the card current usage
        :param card_code: card read numeric code
        :return: current usage card data
        """
        data_out = {
            'card_code': card_code
        }
        card = self.search([('name', '=', card_code)])
        if not card:
            raise UserError(_('Card #%s not found') % card_code)

        data_out['card_id'] = card.id
        data_out['card_categ_id'] = card.card_categ_id.id
        if card.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_P').id:
            # - Product card. We provide input data associated with, if exists
            win = self.env['mdc.data_win'].search([('card_id', '=', card.id), ('wout_id', '=', False)])
            if win:
                data_out['win_lot_id'] = win[0].lot_id.id
                data_out['win_lot_name'] = win[0].lot_id.alias_cp
                data_out['win_weight'] = win[0].weight
                data_out['win_uom'] = win[0].w_uom_id.name
        elif card.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_L').id:
            # - Workstation card. We provide workstation data associated with, if exists
            if card.workstation_id:
                data_out['workstation'] = card.workstation_id.name
        elif card.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_PC').id:
            # - Joker card. We provide lot data associated with, if exists
            if card.lot_id:
                data_out['win_lot_id'] = card.lot_id.id
                data_out['win_lot_name'] = card.lot_id.alias_cp
        elif card.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_O').id:
            # TODO retrieve employee description
            # data_out['employee_code'] = ...
            # data_out['employee_name'] = ...
            pass
        else:
            raise UserError(_('Card not valid (#%s)') % card_code)

        return data_out

    def from_cp_assign_lot(self, values):
        """
        Assign a lot to a card read
        """

        # Data received:
        # - card_code
        # - lot_id
        card = self.search([('name', '=', values['card_code'])])
        if not card:
            raise UserError(_('Card #%s not found') % values['card_code'])
        if card.card_categ_id.id != self.env.ref('mdc.mdc_card_categ_PC').id:
            raise UserError(_('Card #%s is not a joker card!') % values['card_code'])
        card.write({
            'lot_id': values['lot_id'],
        })
        return {
            'card_id': card.id,
            'lot_name': card.lot_id.alias_cp
        }

# ******************************************************************

class Shift(models.Model):
    """
    shift (turn)
    """
    _name = 'mdc.shift'
    _description = 'Shift'

    _sql_constraints = [
        ('shift_code_unique', 'UNIQUE(shift_code)',
         _('Shift_Code has been already assigned to a Shift!')),
    ]

    name = fields.Char(
        'Name',
        required=True)
    shift_code = fields.Char(
        'Shift Code',
        required=True)
    start_time = fields.Float(
        'Start',
        required=True)
    end_time = fields.Float(
        'End',
        required = True)

    @api.multi
    def get_current_shift(self, dt):
        # get current shift: now between start_time and end_time
        shift = False
        if not dt:
            dt = fields.Datetime.now()
        actual_time = fields.Datetime.from_string(dt)  # datetime.datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        time = actual_time.hour + actual_time.minute/60
        shift = self.search([('start_time', '<=', time ), ('end_time', '>', time)])
        if shift:
            start_datetime = fields.datetime(actual_time.year, actual_time.month, actual_time.day, int(shift.start_time), 0, 0)
            end_datetime = fields.datetime(actual_time.year, actual_time.month, actual_time.day, int(shift.end_time), 0, 0)
        else:
            raise UserError(_('We don´t find shift to this time %s') % time)
        return {
            'shift': shift,
            'start_datetime': start_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'end_datetime': end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        }


class CardCateg(models.Model):
    """
    Card Categories
    """
    _sql_constraints = [
        ('card_categ_code_unique', 'UNIQUE(code)',
         _('Card Categ Code has been already assigned to a Card Categ!')),
    ]

    _name = 'mdc.card_categ'
    _description = 'Card Category'

    name = fields.Char(
        'Name',
        required=True)
    code = fields.Char(
        'Code',
        required=True)


class WOutCateg(models.Model):
    """
    Categories for weight output
    """

    _sql_constraints = [
        ('wout_categ_code_unique', 'UNIQUE(code)',
         _('Wout Categ Code has been already assigned to a Wout Categ!')),
    ]
    _name = 'mdc.wout_categ'
    _description = 'wout Category'

    name = fields.Char(
        'Name',
        required=True)
    code = fields.Char(
        'Code',
        required=True)


class Tare(models.Model):
    """
    Tares
    """
    _name = 'mdc.tare'
    _description = 'Tare'

    name = fields.Char(
        'Name',
        required=True)
    tare = fields.Float(
        'Tare',
        required=True)
    uom_id = fields.Many2one(
        'product.uom',
        string = 'Tare Unit')
    active = fields.Boolean(
        'Active',
        default=True)


class Quality(models.Model):
    """
    Quality
    """
    _name = 'mdc.quality'
    _description = 'Quality'

    name = fields.Char(
        'Name',
        required=True)
    code = fields.Integer(
        'Code',
        required=True)
    active = fields.Boolean(
        'Active',
        default=True)


class RfidReader(models.Model):
    '''
    Represents a RFID Reader managed over TCP/IP
    '''
    _name = 'mdc.rfid_reader'
    _description = 'RFID Reader'

    _sql_constraints = [
        ('device_code_unique', 'UNIQUE(device_code)',
         _('Device_Code has been already assigned to a Device!')),
    ]

    name = fields.Char(
        'Name',
        required=True,
        default=_('New RFID device'),
        copy=False)
    device_code = fields.Char(
        'Device Code',
        required=True,
        default='0',
        copy=False)
    tcp_address_ip = fields.Char(
        'IP Address',
        copy=False)
    tcp_address_port = fields.Integer(
        'IP Port')
    active = fields.Boolean(
        'Active',
        default=True)