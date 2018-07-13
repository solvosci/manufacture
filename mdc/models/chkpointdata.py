# -*- coding: utf-8 -*-

import socket
from odoo import api, models, fields, _
from odoo.exceptions import UserError

class DataWIn(models.Model):
    """
    Main data for a chkpoint_datacapture weight input
    """
    _name = 'mdc.data_win'
    _description = 'Weight Input Data'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    def _get_card_id_domain(self):
        # TODO add filter "card is not in use"
        return [('card_categ_id', '=', self.env.ref('mdc.mdc_card_categ_P').id)]

    def _get_w_uom_id_domain(self):
        return [('category_id', '=', self.env.ref('product.product_uom_categ_kgm').id)]

    line_id = fields.Many2one(
        'mdc.line',
        string='Line',
        required=True)
    lot_id = fields.Many2one(
        'mdc.lot',
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
        default=0,
        required=True)
    w_uom_id = fields.Many2one(
        'product.uom',
        string='Weight UoM',
        required=True,
        domain=_get_w_uom_id_domain)
    card_id = fields.Many2one(
        'mdc.card',
        string='Card',
        required=True,
        domain=_get_card_id_domain)
    wout_id = fields.Many2one(
        'mdc.data_wout',
        string='WOut')

    @api.model
    def create(self, values):
        data_win_card = self.search([('wout_id', '=', False), ('card_id', '=', values['card_id'])])
        if data_win_card:
            raise UserError(_('There is already open data with the selected card (%s)') % data_win_card[0].card_id.name)

        return super(DataWIn, self).create(values)

    def from_cp_create(self, values):
        '''
        Saves a checkpoint entry from some input data
        '''

        # Data received:
        # - checkpoint_id.id
        # - card_code

        chkpoint = self.env['mdc.chkpoint'].browse(values['chkpoint_id'])
        if not chkpoint:
            raise UserError(_('Checkpoint #%s not found') % values['chkpoint_id'])
        if not chkpoint.current_lot_active_id:
            raise UserError(_("There's not an active lot"))
        if not chkpoint.scale_id:
            raise UserError(_("Scale not defined"))
        if not chkpoint.tare_id:
            raise UserError(_("Tare not defined"))
        try:
            weight_value, weight_uom_id = chkpoint.scale_id.get_weight()[0:2]
        except socket.timeout:
            raise UserError(_("Timed out on weighing scale"))

        card = self.env['mdc.card'].search([('name', '=', values['card_code'])])
        if not card:
            raise UserError(_("Card #%s not found") % values['card_code'])
        if card.card_categ_id.id != self.env.ref('mdc.mdc_card_categ_P').id:
            raise UserError(_("Invalid Card #%s") % values['card_code'])

        return self.create({
            'line_id': chkpoint.line_id.id,
            'lot_id': chkpoint.current_lot_active_id.id,
            'tare': chkpoint.tare_id.tare,
            'weight': weight_value,
            'w_uom_id': weight_uom_id.id,
            'card_id': card.id
        })


class DataWOut(models.Model):
    """
    Main data for a chkpoint_datacapture weight input
    """
    _name = 'mdc.data_wout'
    _description = 'Weight Output Data'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    def _get_w_uom_id_domain(self):
        return [('category_id', '=', self.env.ref('product.product_uom_categ_kgm').id)]

    line_id = fields.Many2one(
        'mdc.line',
        string='Line',
        required=True)
    lot_id = fields.Many2one(
        'mdc.lot',
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
        default=0,
        required=True)
    w_uom_id = fields.Many2one(
        'product.uom',
        string='Weight UoM',
        required=True,
        domain=_get_w_uom_id_domain)
    quality_id = fields.Many2one(
        'mdc.quality',
        string='Quality',
        required=True)
    card_ids = fields.Many2many(
        'mdc.card',
        string='Card')
    workstation_id = fields.Many2one(
        'mdc.workstation',
        string='Workstation',
        required=True)
    shift_id = fields.Many2one(
        'mdc.shift',
        string='Shift',
        required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True)
    shared = fields.Boolean(
        string='Shared',
        default=False)
    wout_shared_id =fields.Many2one(
        'mdc.data_wout',
        string='Shared with')
    wout_categ_id = fields.Many2one(
        'mdc.wout_categ',
        string='Out Category',
        required=True)
    gross_weight = fields.Float(
        'Gross Weight',
        readonly=True,
        default=0)

    @api.onchange('card_ids')
    def _retrieve_workstation_card_data(self):

        for dataWOut in self:
            #search workstation card
            for card_id in dataWOut.card_ids:
                card = self.env['mdc.card'].search([('id', '=', card_id.id), ('workstation_id', '!=', False)])
                if card:
                    dataWOut.workstation_id = card.workstation_id.id
                    dataWOut.shift_id = card.workstation_id.shift_id.id
                    dataWOut.employee_id = card.workstation_id.current_employee_id.id


    @api.model
    def create(self, values):
        gross_weight = 0.0

        #retrive all card ids
        card_ids = [] if len(values.get('card_ids')) == 0 else values.get('card_ids')[0][2]

        #var to store data_win ids of cards
        ids_win = []
        current_lot_id = None

        if len(card_ids) > 0:
            cards = self.env['mdc.card'].browse(card_ids)
            for card in cards:
                # Product card
                if card.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_P').id:
                    data_win = self.env['mdc.data_win'].search([('card_id', '=', card.id), ('wout_id', '=', False)])
                    if data_win:
                        if current_lot_id and current_lot_id.id != data_win.lot_id.id:
                            raise UserError(_("Card #%s comes from a different lot (current: %s)") %
                                            (card.name, current_lot_id.name))
                        current_lot_id = data_win.lot_id
                        gross_weight += data_win.weight - data_win.tare
                        ids_win.append(data_win.id)
                    else:
                        raise UserError(_("Card #%s not valid: there's not open input data linked with") % card.name)
                # Workstation card
                elif card.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_L').id:
                    if card.workstation_id.current_employee_id:
                        values['employee_id'] = card.workstation_id.current_employee_id.id
                    else:
                        raise UserError(_("Card #%s not valid: there's not any employee assigned with") % card.name)
                    values['workstation_id'] = card.workstation_id.id
                    values['shift_id'] = card.workstation_id.shift_id.id
                else:
                    # TODO other card types (e.g. "joker" card, employee card....)
                    # TODO scrumbs management
                    raise UserError(_("Unknown card #%s") % card.name)

        values['gross_weight'] = gross_weight
        # TODO Lot should be filled from view for testing purposes. Actually, it should always be computed
        if current_lot_id:
            values['lot_id'] = current_lot_id.id

        data_wout = super(DataWOut, self).create(values)

        # Close data_win entries
        """
        for id in ids_win:
            data_win = self.env['mdc.data_win'].search([('id', '=', id)])
            if data_win:
                data_win.write({
                    'wout_id': data_wout.id,
                })
        """
        if len(ids_win) > 0:
            data_win = self.env['mdc.data_win'].browse(ids_win)
            if data_win:
                data_win.write({
                    'wout_id': data_wout.id
                })

        return data_wout

    def from_cp_create(self, values):
        '''
        Saves a checkpoint entry from some input data
        '''

        # Data received:
        # - checkpoint_id
        # - cards_in
        # - card_workstation
        # - quality_id

        chkpoint = self.env['mdc.chkpoint'].browse(values['chkpoint_id'])
        if not chkpoint:
            raise UserError(_('Checkpoint #%s not found') % values['chkpoint_id'])
        if not chkpoint.scale_id:
            raise UserError(_("Scale not defined"))
        if not chkpoint.tare_id:
            raise UserError(_("Tare not defined"))
        try:
            weight_value, weight_uom_id = chkpoint.scale_id.get_weight()[0:2]
        except socket.timeout:
            raise UserError(_("Timed out on weighing scale"))

        cards_id_list = [] if len(values['cards_in']) == 0 else [card['card_id'] for card in values['cards_in']]
        cards_id_list.append(values['card_workstation']['card_id'])
        card_ids = [(6, False, cards_id_list)]

        return self.create({
            'line_id': chkpoint.line_id.id,
            'lot_id': chkpoint.current_lot_active_id.id,
            'tare': chkpoint.tare_id.tare,
            'weight': weight_value,
            'w_uom_id': weight_uom_id.id,
            'quality_id': values['quality_id'],
            'wout_categ_id': values['wout_categ_id'],
            'card_ids': card_ids
        })


