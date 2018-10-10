from odoo import api, fields, models, exceptions


class MdcConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'mdc.config.settings'

    rfid_server_url = fields.Char('RFID Server URL')
    rfid_server_user = fields.Char('RFID Server User')
    rfid_server_password = fields.Char('RFID Server Password')
    rfid_ws_server_url = fields.Char('RFID WebSocket Server URL')
    lot_default_life_days = fields.Char('Lots default life in days')

    @api.model
    def get_values(self):
        res = super(MdcConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        res.update(
            rfid_server_url=IrConfigParameter.get_param('mdc.rfid_server_url'),
            rfid_server_user=IrConfigParameter.get_param('mdc.rfid_server_user'),
            rfid_server_password=IrConfigParameter.get_param('mdc.rfid_server_password'),
            rfid_ws_server_url=IrConfigParameter.get_param('mdc.rfid_ws_server_url'),
            lot_default_life_days=IrConfigParameter.get_param('mdc.lot_default_life_days')
        )
        return res

    @api.multi
    def set_values(self):
        super(MdcConfigSettings, self).set_values()
        if not self.user_has_groups('mdc.group_mdc_office_worker'):
            raise exceptions.UserError(_('You are not allowed to change this values'))
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        IrConfigParameter.set_param('mdc.rfid_server_url', self.rfid_server_url)
        IrConfigParameter.set_param('mdc.rfid_server_user', self.rfid_server_user)
        IrConfigParameter.set_param('mdc.rfid_server_password', self.rfid_server_password)
        IrConfigParameter.set_param('mdc.rfid_ws_server_url', self.rfid_ws_server_url)
        IrConfigParameter.set_param('mdc.lot_default_life_days', self.lot_default_life_days)

