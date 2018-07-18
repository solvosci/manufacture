
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class Employee(models.Model):
    _inherit = 'hr.employee'

    def _default_employee_code(self):
        last_code = self.search([('employee_code', 'like', 'OPE%')], order='employee_code desc', limit=1)
        code_max_num = 1
        if last_code:
            code_max_num = int(last_code.employee_code[4:]) + 1
        return 'OPE ' + str(code_max_num).zfill(4)

    employee_code = fields.Char('Employee code', required=False, default=_default_employee_code)
    contract_type_id = fields.Many2one('hr.contract.type', string="Contract Type", required=True,
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    workstation_id = fields.One2many(
        'mdc.workstation',
        'current_employee_id')
    worksheets_count = fields.Integer(compute='_compute_worksheets_count', string='Worksheets')
    present = fields.Boolean(
        'Present',
        readonly=True,
        compute='_compute_present',
        store=True)

    def _compute_worksheets_count(self):
        # read_group as sudo, since worksheet count is displayed on form view
        worksheet_data = self.env['mdc.worksheet'].sudo().read_group([('employee_id', 'in', self.ids)], ['employee_id'],
                                                                  ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in worksheet_data)
        for employee in self:
            employee.worksheets_count = result.get(employee.id, 0)

    @api.multi
    def _compute_present(self):
        # FIXME does NOT compute yet => link model with employee worksheets and add @api.depends
        worksheet_data = self.env['mdc.worksheet'].sudo().read_group(
            [('employee_id', 'in', self.ids), ('end_datetime', '=', False)],
            ['employee_id'],
            ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in worksheet_data)
        for employee in self:
            employee.present = True if result.get(employee.id, 0) > 0 else False

    @api.model
    def create(self, values):
        _logger.info("[SLV] Employee_create")
        #values['employee_code'] = self._default_employee_code()
        return super(Employee, self).create(values)