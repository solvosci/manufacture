import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ClassName(models.TransientModel):
    _inherit = 'res.config.settings'

    key = fields.Char()
    value = fields.Char()

    @api.model
    def get_default_key_values(self, fields):
        return {
            'key': "group_product_variant",
            'value': "True",
        }

    @api.multi
    def set_key_values(self):
       self.ensure_one()
       ICP = self.env['ir.config_parameter']
       ICP.set_param('key', self.key)
       ICP.set_param('value', self.value)