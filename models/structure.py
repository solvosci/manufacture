# -*- coding: utf-8 -*-

import datetime
from odoo import api, models, fields, _
from odoo.exceptions import UserError

class BaseStructure(models.AbstractModel):
    """
    Allocates common functionality for Structure modules
    """
    _name = 'slv.mdc.base.structure'
    _description = 'Base Structure model'

    def _get_chkpoint_categ_selection(self):
        return [
            ('W_IN', _('Input')),
            ('W_OUT', _('Output')),
    ]

    def _get_card_status_selection(self):
        return [
            ('USE', _('In Use')),
            ('IDLE', _('Idle')),
            ('BLOCKED', _('Bloked'))
    ]
    

class Line(models.Model):
    """
    Main data for a line
    """
    _name = 'slv.mdc.line'
    _description = 'Line'

    name = fields.Char(
        'Name',
        required=True)


class ChkPoint(models.Model):
    """
    Main data for a chkpoint (check points)
    """
    _name = 'slv.mdc.chkpoint'
    _inherit = ['slv.mdc.base.structure']
    _description = 'Check Point'

    name = fields.Char(
        'Name',
        required=True)
    chkpoint_categ = fields.Selection(
        selection='_get_chkpoint_categ_selection',
        string='Checkpoint Category')
    line_id = fields.Many2one(
        'slv.mdc.line',
        string='Line',
        required=True)
    order =fields.Integer(
        'order',
        required=True)
    scale_id = fields.Many2one(
        'slv.mdc.scale',
        string='Scale')
    rfid_reader_id = fields.Many2one(
        'slv.mdc.rfid_reader',
        string='RFID Reader')
    tare = fields.Many2one(
        'slv.mdc.tare',
        string='Tare')
    quality_id = fields.Many2one(
        'slv.mdc.quality',
        string='Quality')


class Workstation(models.Model):
    """
    Main data for a workstation
    """
    _name = 'slv.mdc.workstation'
    _inherit = ['slv.mdc.base.structure']
    _description = 'Workstation'

    name = fields.Char(
        'Name',
        required=True)
    line_id = fields.Many2one(
        'slv.mdc.line',
        string='Line',
        required=True)
    shift_id = fields.Many2one(
        'slv.mdc.shift',
        string='Shift',
        required=True)
    seat = fields.Integer(
        'Seat',
        required=True)
    current_employee_id = fields.Many2one(
        'hr.employee',
        string = 'Employee')


class Card(models.Model):
    """
    Main data for a cards
    """
    _name = 'slv.mdc.card'
    _inherit = ['slv.mdc.base.structure']
    _description = 'Card'

    name = fields.Integer(
        'Card_Code',
        required=True)
    card_categ_id = fields.Many2one(
        'slv.mdc.card_categ',
        string='Card_Categ',
        required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string = 'Employee')
    workstation_id = fields.Many2one(
        'slv.mdc.workstation',
        string='Workstation')
    status = fields.Selection(
        selection='_get_card_status_selection',
        string='Status')


# ******************************************************************

class Shift(models.Model):
    """
    shift (turn)
    """
    _name = 'slv.mdc.shift'
    _description = 'Shift'

    name = fields.Char(
        'Name',
        required=True)


class CardCateg(models.Model):
    """
    Card Categories
    """
    _name = 'slv.mdc.card_categ'
    _description = 'Card Category'

    name = fields.Char(
        'Name',
        required=True)


class WOutCateg(models.Model):
    """
    Categories for weight output
    """
    _name = 'slv.mdc.w_out_categ'
    _description = 'w_out Category'

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
    _name = 'slv.mdc.tare'
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
    _name = 'slv.mdc.quality'
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
    _name = 'slv.mdc.rfid_reader'
    _description = 'RFID Reader'

    name = fields.Char(
        'Name',
        required=True)
    tcp_address_ip = fields.Char(
        'IP Address',
        required=True)
    tcp_address_port = fields.Integer(
        'IP Port',
        required=True)
    active = fields.Boolean(
        'Active',
        default=True)