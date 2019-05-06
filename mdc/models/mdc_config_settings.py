from odoo import api, fields, models, exceptions, _


class MdcConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'mdc.config.settings'

    rfid_server_url = fields.Char('RFID Server URL')
    rfid_server_user = fields.Char('RFID Server User')
    rfid_server_password = fields.Char('RFID Server Password')
    rfid_ws_server_url = fields.Char('RFID WebSocket Server URL')
    rfid_server_min_secs_between_worksheets = fields.Char('RFID Server minimum seconds between worksheets')
    rfid_server_last_worksheet_timestamp = fields.Char('RFID Server last worksheet timestamp')
    lot_default_life_days = fields.Char('Lots default life in days')
    lot_last_total_gross_weight_update_timestamp = fields.Char('Lot last total gross weight update timestamp')

    @api.model
    def get_values(self):
        res = super(MdcConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        res.update(
            rfid_server_url=IrConfigParameter.get_param('mdc.rfid_server_url'),
            rfid_server_user=IrConfigParameter.get_param('mdc.rfid_server_user'),
            rfid_server_password=IrConfigParameter.get_param('mdc.rfid_server_password'),
            rfid_ws_server_url=IrConfigParameter.get_param('mdc.rfid_ws_server_url'),
            rfid_server_min_secs_between_worksheets=IrConfigParameter.get_param('mdc.rfid_server_min_secs_between_worksheets'),
            rfid_server_last_worksheet_timestamp=IrConfigParameter.get_param('mdc.rfid_server_last_worksheet_timestamp'),
            lot_default_life_days=IrConfigParameter.get_param('mdc.lot_default_life_days'),
            lot_last_total_gross_weight_update_timestamp=IrConfigParameter.get_param('mdc.lot_last_total_gross_weight_update_timestamp'),
        )
        return res

    @api.multi
    def set_values(self):
        super(MdcConfigSettings, self).set_values()

        if not self.user_has_groups('mdc.group_mdc_office_worker'):
            raise exceptions.UserError(_('You are not allowed to change this values'))
        try:
            min_secs = int(self.rfid_server_min_secs_between_worksheets)
        except ValueError as ve:
            raise models.ValidationError(_('The minimum seconds between worksheets must be an integer!!'))
        if min_secs <= 0:
            raise models.ValidationError(_('The minimum seconds between worksheets must be bigger than 0!!!'))

        try:
            lot_days = int(self.lot_default_life_days)
        except ValueError as ve:
            raise models.ValidationError(_('The lot default life days must be an integer!!'))
        if lot_days < 0:
            raise models.ValidationError(_('The lot default life days must be at least zero!!!'))

        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        IrConfigParameter.set_param('mdc.rfid_server_url', self.rfid_server_url)
        IrConfigParameter.set_param('mdc.rfid_server_user', self.rfid_server_user)
        IrConfigParameter.set_param('mdc.rfid_server_password', self.rfid_server_password)
        IrConfigParameter.set_param('mdc.rfid_ws_server_url', self.rfid_ws_server_url)
        IrConfigParameter.set_param('mdc.rfid_server_min_secs_between_worksheets', self.rfid_server_min_secs_between_worksheets)
        IrConfigParameter.set_param('mdc.lot_default_life_days', self.lot_default_life_days)

