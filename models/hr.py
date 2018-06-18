from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    workstation_id = fields.One2many(
        'slv.mdc.workstation',
        'current_employee_id')