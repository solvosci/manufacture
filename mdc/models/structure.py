# -*- coding: utf-8 -*-

import datetime
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

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
         'Line_Code has been already assigned to a Line!'),
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
         'Combination: Line & Checkpoint category, are unique, and already Exists!'),
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


class Workstation(models.Model):
    """
    Main data for a workstation
    """
    _name = 'mdc.workstation'
    _inherit = ['mdc.base.structure']
    _description = 'Workstation'

    _sql_constraints = [
        ('current_employee_unique', 'UNIQUE(current_employee_id)',
         'The employee has been already assigned to a workstation!'),
    ]

    name = fields.Char(
        'Name',
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
        string = 'Employee',
        index=True,
        ondelete='cascade',
        domain=[('workstation_id', '=', False)])


class Card(models.Model):
    """
    Main data for a cards
    """
    _name = 'mdc.card'
    _inherit = ['mdc.base.structure']
    _description = 'Card'

    name = fields.Integer(
        'Card_Code',
        required=True)
    card_categ_id = fields.Many2one(
        'mdc.card_categ',
        string='Card_Categ',
        required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string = 'Employee')
    workstation_id = fields.Many2one(
        'mdc.workstation',
        string='Workstation')
    status = fields.Selection(
        selection='_get_card_status_selection',
        string='Status')


# ******************************************************************

class Shift(models.Model):
    """
    shift (turn)
    """
    _name = 'mdc.shift'
    _description = 'Shift'

    _sql_constraints = [
        ('shift_code_unique', 'UNIQUE(shift_code)',
         'Shift_Code has been already assigned to a Shift!'),
    ]

    name = fields.Char(
        'Name',
        required=True)
    shift_code = fields.Char(
        'Shift Code',
        required=True)


class CardCateg(models.Model):
    """
    Card Categories
    """
    _name = 'mdc.card_categ'
    _description = 'Card Category'

    name = fields.Char(
        'Name',
        required=True)


class WOutCateg(models.Model):
    """
    Categories for weight output
    """
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


class Quality(models.Model):
    """
    Quality
    """
    _name = 'mdc.quality'
    _description = 'Quality'

    name = fields.Char(
        'Code',
        required=True)
    descrip = fields.Char(
        'Description',
        required=True)

class RfidReader(models.Model):
    '''
    Represents a RFID Reader managed over TCP/IP
    '''
    _name = 'mdc.rfid_reader'
    _description = 'RFID Reader'

    _sql_constraints = [
        ('device_code_unique', 'UNIQUE(device_code)',
         'Device_Code has been already assigned to a Device!'),
    ]

    name = fields.Char(
        'Name',
        required=True)
    device_code = fields.Char(
        'Device Code',
        required=True)
    tcp_address_ip = fields.Char(
        'IP Address')
    tcp_address_port = fields.Integer(
        'IP Port')
    active = fields.Boolean(
        'Active',
        default=True)