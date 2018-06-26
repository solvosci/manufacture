
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_code = fields.Char('Employee code')
    contract_type_id = fields.Many2one('hr.contract.type', string="Contract Type", required=True,
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    workstation_id = fields.One2many(
        'mdc.workstation',
        'current_employee_id')

    def _default_employee_code(self):
        last_code = self.search([('employee_code', 'like', 'OPE%')], order='employee_code desc', limit=1)
        code_max_num = 1
        if last_code:
            code_max_num = int(last_code.employee_code[4:]) + 1
        return 'OPE ' + str(code_max_num).zfill(4)

    @api.model
    def create(self, values):
        _logger.info("[SLV] Employee_create")
        values['employee_code'] = self._default_employee_code()
        return super(Employee, self).create(values)