# -*- coding: utf-8 -*-

import datetime as dt
import logging
import socket
from odoo import api, models, fields, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF

_logger = logging.getLogger(__name__)


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
    active = fields.Boolean(
        'Active',
        default=True)

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

    @api.multi
    def cancel_input(self):
        """
        Cancels (if possible) the current input data
        :return:
        """
        for w in self:
            if w.wout_id:
                raise UserError(_("Cannot cancel input '%s - %s - %s' because it's been already linked with an output")
                                % (w.line_id.name, w.lot_id.name, w.create_datetime))
            w.write({'active': False})
            _logger.info('[mdc.data_win] Cancelled input %s - %s - %s' % (w.line_id.name, w.lot_id.name, w.create_datetime))

    def get_average_data(self, context):
        """
        Obtains average data for the given context (e.g. line_id and lot_id)
        """
        w_create_datetime = None
        w_tare = None
        w_uom_id = None
        w_weight = 0
        w_numwin = 0
        w_timewout = 0
        w_numwout = 0
        win_lots = self.search([('line_id', '=', context['line_id']), ('lot_id', '=', context['lot_id'])],
                               order='create_datetime asc')
        if win_lots:
            for wi in win_lots:
                if w_tare is None:
                    w_tare = wi.tare
                    w_uom_id = wi.w_uom_id.id
                # if we don´t find any wout we have the first create_datetime
                if w_create_datetime is None:
                    w_create_datetime = wi.create_datetime
                # just keep in mind records with the same tare
                if wi.tare == w_tare and wi.w_uom_id.id == w_uom_id:
                    w_weight += wi.weight
                    w_numwin += 1
                    _logger.info('[mdc.data_win] _calculate_lot_average_data WIN %s - weight: %s ' %
                                 (w_numwin, wi.weight))
                # to calculate create_datetime we need the create_datetime of the wout
                if wi.wout_id is not None:
                    # retrieve the wout record
                    wo = self.env['mdc.data_wout'].browse(wi.wout_id.id)
                    if wo:
                        w_numwout += 1
                        difference = dt.datetime.strptime(wo.create_datetime, '%Y-%m-%d %H:%M:%S') - \
                                     dt.datetime.strptime(wi.create_datetime, '%Y-%m-%d %H:%M:%S')
                        dif_hours = difference.days * 24 + difference.seconds / 3600
                        w_timewout += dif_hours
                        _logger.info(
                            '[mdc.data_win] get_average_data WOUT %s - datetime_in: %s - datetime_out: %s - diff.: %s'
                            % (w_numwout, wi.create_datetime, wo.create_datetime, dif_hours))

        # calculate de average of the weight
        if w_numwin > 0:
            w_weight = w_weight / w_numwin
        # calculate de average of the timewout
        # if we don´t find any wout we have the first create_datetime
        if w_numwout > 0:
            w_timewout = w_timewout / w_numwout
            ww_create_datetime = dt.datetime.now() - dt.timedelta(hours=w_timewout)
            w_create_datetime = ww_create_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # return data to create de joker win reg
        _logger.info('[mdc.data_win] _calculate_lot_average_data to lot id %s and line id %s: '
                     'avg_time: %s - numwout: % s - create_datetime: %s - '
                     'numwin:%s - tare: %s - weight: %s - uom: %s'
                     % (context['lot_id'], context['line_id'], w_timewout, w_numwout, w_create_datetime, w_numwin,
                        w_tare, w_weight, w_uom_id))
        return {
            'create_datetime': w_create_datetime or fields.Datetime.now(),
            'tare': w_tare,
            'weight': w_weight,
            'w_uom_id': w_uom_id
        }

    def _cancel_expired_inputs(self):
        """
        Cancels all the inputs created at least a day ago and not yet linked with an output
        :return:
        """
        expiration_date = dt.datetime.now() + dt.timedelta(days=-1)
        cancellable_inputs = self.search([('wout_id', '=', False),
                                          ('create_datetime', '<=', expiration_date.strftime(DF))])
        if cancellable_inputs:
            try:
                cancellable_inputs.cancel_input()
            except UserError as e:
                _logger.error('[mdc.data_win] _cancel_expired_inputs:  %s' % e)


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
                elif card.card_categ_id.id == self.env.ref('mdc.mdc_card_categ_PC').id:
                    # Joker card. Prior to create the output we should make a related input
                    # Conventions:
                    # - There isn't lot validation (we take the output one)
                    # FIXME Tare: WOUT checkpoint tare, not the WIN one! Should associate a tare with every joker card?
                    # - weight: the current average for the lot
                    # FIXME w_uom_id: we don't know how to fill, then we take the WOUT scale
                    """
                    joker_win = self.env['mdc.data_win'].create({
                        'line_id': values['line_id'],
                        'lot_id': values['lot_id'],
                        'tare': values['tare'],
                        'weight': self.env['mdc.lot'].browse(values['lot_id']).get_input_avg_weight(),
                        'w_uom_id': values['w_uom_id'],
                        'card_id': card.id
                    })
                    """
                    joker_win_data = self.env['mdc.data_win'].get_average_data({
                        'lot_id': values['lot_id'], 'line_id': values['line_id']})
                    joker_win_data['lot_id'] = values['lot_id']
                    joker_win_data['line_id'] = values['line_id']
                    joker_win_data['card_id'] = card.id
                    joker_win = self.env['mdc.data_win'].create(joker_win_data)
                    ids_win.append(joker_win.id)
                else:
                    # TODO other card types (e.g. employee card....)
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
        # - wout_categ_code
        wout_categ_id = self.env['mdc.wout_categ'].search([('code', '=', values['wout_categ_code'])])
        if not wout_categ_id:
            raise UserError(_('WOUT categ code #%s not found') % values['wout_categ_code'])
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
            # TODO select from cards_id_list!!!!
            'lot_id': chkpoint.current_lot_active_id.id,
            'tare': chkpoint.tare_id.tare,
            'weight': weight_value,
            'w_uom_id': weight_uom_id.id,
            'quality_id': values['quality_id'],
            'wout_categ_id': wout_categ_id.id,
            'card_ids': card_ids
        })


