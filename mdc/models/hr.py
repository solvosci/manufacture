
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import datetime as DT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DF

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
    worksheet_start_datetime = fields.Datetime(
        'Worksheet Start Datetime',
        readonly=True,
        compute='_compute_worksheet_data',
        store=True)
    worksheet_end_datetime = fields.Datetime(
        'Worksheet End Datetime',
        readonly=True,
        compute='_compute_worksheet_data',
        store=True)
    worksheet_status_start_datetime = fields.Datetime(
        'Worksheet Status Start Datetime',
        readonly=True,
        compute='_compute_worksheet_data',
        store=True)
    worksheet_status_data = fields.Char(
        'Worksheet Status data',
        readonly=True,
        compute='_compute_worksheet_data',
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

    @api.multi
    @api.depends('worksheet_ids.end_datetime')
    def _compute_worksheet_data(self):
        # TODO check filtered performance when growing data
        for employee in self:
            # compute the last start datetime (the start date time real of worksheet, not change of status)
            last_start_datetime_real = None
            # compute the last end datetime (to use to validate on create and write a worksheet)
            last_end_datetime = None
            # compute the last start datetime (to built worksheet status = last start date opened + lot + workstation)
            last_start_datetime = None
            worksheet_data_status = None
            # to do this we need de last worksheet of te employee
            #TODO: find another way to do this -> find another way withour limit
            we = self.env['mdc.worksheet'].search([('employee_id', '=', employee.id)]
                                                  , order='start_datetime desc', limit=100)
            for ws in we:
                if last_start_datetime_real is None:
                    last_start_datetime_real = ws.start_datetime
                else:
                    # while end_datetime = last start date time is not the real start date time
                    if str(ws.end_datetime) == str(last_start_datetime_real):
                        last_start_datetime_real = ws.start_datetime
                    else:
                        break
                if last_end_datetime is None and ws.end_datetime is not False:
                    last_end_datetime = ws.end_datetime
                if worksheet_data_status is None and ws.end_datetime is False:
                    last_start_datetime = ws.start_datetime
                    worksheet_data_status = '%s - %s ' % (ws.lot_id.name or '', ws.workstation_id.name or '')

            # set the calculated values
            employee.worksheet_start_datetime = last_start_datetime_real
            employee.worksheet_end_datetime = last_end_datetime
            employee.worksheet_status_start_datetime = last_start_datetime
            employee.worksheet_status_data = worksheet_data_status


    @api.model
    def create(self, values):
        _logger.info("[SLV] Employee_create")

        if values.get('operator') and not values.get('employee_code'):
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

    @api.multi
    def worksheet_open(self, start_datetime):
        self.ensure_one()
        if self.present:
            raise UserError(_('Cannot create open worksheet: employee %s is already present') % self.employee_code)
        self.env['mdc.worksheet'].create({
            'start_datetime': start_datetime,
            'employee_id': self.id})

    @api.multi
    def worksheet_close(self, end_datetime):
        self.ensure_one()
        if not self.present:
            raise UserError(_('Cannot create close worksheet: employee %s is not present') % self.employee_code)
        self.worksheet_ids.filtered(lambda r: r.end_datetime is False).write({'end_datetime': end_datetime})
        # TODO check filtered performance when growing data. If decreases, use the code above
        """
        Worksheet = self.env['mdc.worksheet'].search(
            [('end_datetime', '=', False),
             ('employee_id', '=', self.id)])
        Worksheet.write({'end_datetime': self.end_datetime})
        """

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

    def massive_worksheet_close(self):
        Wizard = self.env['hr.employee.massworksheetclose.wizard']
        new = Wizard.create({
            'employee_ids': [(6, False, self._context['active_ids'])]
        })
        return {
            'name': 'Massive worksheet close',
            'res_model': 'hr.employee.massworksheetclose.wizard',
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


class EmployeeMassWorksheetClose(models.TransientModel):
    _name = 'hr.employee.massworksheetclose.wizard'
    _description = 'Employee massive worksheet close wizard'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()

    end_datetime = fields.Datetime(
        'End Datetime',
        required=True,
        default=_default_date)
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Employees')

    @api.model
    def create(self, values):
        # TODO
        return super(EmployeeMassWorksheetClose, self).create(values)

    def action_save(self):
        self.ensure_one()
        for employee in self.employee_ids:
            if not employee.present:
                # TODO improve not present employee detection (e.g. display ALL present employees)
                raise UserError(_('Cannot create close worksheet: employee %s is not present')
                                % employee.employee_code)
            Worksheet = self.env['mdc.worksheet'].search(
                [('end_datetime', '=', False),
                 ('employee_id', '=', employee.id)])
            Worksheet.write({'end_datetime': self.end_datetime})

    def action_cancel(self):
        return True
