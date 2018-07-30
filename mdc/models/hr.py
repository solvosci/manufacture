
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class Employee(models.Model):
    _inherit = 'hr.employee'

    _sql_constraints = [
        ('employee_code_unique', 'UNIQUE(employee_code)',
         _('Employee code must be unique!')),
    ]

    def _default_employee_code(self):
        last_code = self.search([('employee_code', 'like', 'OPE%')], order='employee_code desc', limit=1)
        code_max_num = 1
        if last_code:
            code_max_num = int(last_code.employee_code[4:]) + 1
        return 'OPE ' + str(code_max_num).zfill(4)

    operator = fields.Boolean('Is operator', required=True, default=False)
    employee_code = fields.Char('Employee code', required=False)
    contract_type_id = fields.Many2one('hr.contract.type', string="Contract Type",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))
    workstation_id = fields.One2many(
        'mdc.workstation',
        'current_employee_id')
    worksheets_count = fields.Integer(compute='_compute_worksheets_count', string='Worksheets')
    worksheet_ids = fields.One2many(
        'mdc.worksheet',
        'employee_id')
    present = fields.Boolean(
        'Present',
        readonly=True,
        compute='_compute_present',
        store=True)

    def _compute_worksheets_count(self):
        """
        # read_group as sudo, since worksheet count is displayed on form view
        worksheet_data = self.env['mdc.worksheet'].sudo().read_group([('employee_id', 'in', self.ids)], ['employee_id'],
                                                                  ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in worksheet_data)
        for employee in self:
            employee.worksheets_count = result.get(employee.id, 0)
        """
        # TODO check count performance when growing data. If decreases, use the code above
        for employee in self:
            employee.worksheets_count = len(employee.worksheet_ids)

    @api.multi
    @api.depends('worksheet_ids.end_datetime')
    def _compute_present(self):
        """
        worksheet_data = self.env['mdc.worksheet'].sudo().read_group(
            [('employee_id', 'in', self.ids), ('end_datetime', '=', False)],
            ['employee_id'],
            ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in worksheet_data)
        for employee in self:
            employee.present = True if result.get(employee.id, 0) > 0 else False
        """
        # TODO check filtered performance when growing data. If decreases, use the code above
        for employee in self:
            employee.present = len(employee.worksheet_ids.filtered(lambda r: r.end_datetime is False)) > 0


    @api.model
    def create(self, values):
        _logger.info("[SLV] Employee_create")

        if values['operator'] and not values['employee_code']:
            values['employee_code'] = self._default_employee_code()

        return super(Employee, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()
        if 'operator' in values:
            if values['operator'] and not self.employee_code and not 'employee_code' in values:
                # Employee is now an operator and his employee code is not set
                values['employee_code'] = self._default_employee_code()
            if not values['operator']:
                # Employee is no longer an operator, then employee code and contract type must be removed
                values['employee_code'] = False
                values['contract_type_id'] = False
        else:
            if 'employee_code' in values and not values['employee_code']:
                raise UserError(_("It's not allowed to delete employee code for an operator. "
                                  "If you want to set an automatic code, first unset operator check and save"))

        return super(Employee, self).write(values)

    def massive_worksheet_open(self):
        Wizard = self.env['hr.employee.massworksheetopen.wizard']
        new = Wizard.create({
            'employee_ids': [(6, False, self._context['active_ids'])]
        })
        return {
            'name': 'Massive worksheet open',
            'res_model': 'hr.employee.massworksheetopen.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new.id,
            'target': 'new',
            'type': 'ir.actions.act_window'
        }


class EmployeeMassWorksheetOpen(models.TransientModel):
    _name = 'hr.employee.massworksheetopen.wizard'
    _description = 'Employee massive worksheet open wizard'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    start_datetime = fields.Datetime(
        'Start Datetime',
        required=True,
        default=_default_date)
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees')

    @api.model
    def create(self, values):
        # TODO
        return super(EmployeeMassWorksheetOpen, self).create(values)

    def action_save(self):
        self.ensure_one()
        Worksheet = self.env['mdc.worksheet']
        for employee in self.employee_ids:
            if employee.present:
                # TODO improve present employee detection (e.g. display ALL present employees)
                raise UserError(_('Cannot create open worksheet: employee %s is already present')
                                % employee.employee_code)
            Worksheet.create({
                'start_datetime': self.start_datetime,
                'employee_id': employee.id})

    def action_cancel(self):
        return True
