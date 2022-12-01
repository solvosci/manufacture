from datetime import date, datetime
from odoo import api, models, fields, _
import socket

class DataCrumbs(models.Model):
    """
    Main data for a crumb cleaning
    """
    _name = 'mdc.data_crumbs'
    _description = 'Crumbs cleaning Data'

    def _default_date(self):
        #return fields.Datetime.from_string(fields.Datetime.now())
        return fields.Datetime.now()
    def _default_uom(self):
        return self.env.ref('product.product_uom_kgm')
    def _get_w_uom_id_domain(self):
        return [('category_id', '=', self.env.ref('product.product_uom_categ_kgm').id)]
    def _get_chkpoint_id_domain(self):
        return [('chkpoint_categ', '=', 'CRUMBS')]
    def _get_workstation_id_domain(self):
        return [('crumbs_seat', '=', True)]

    line_id = fields.Many2one(
        'mdc.line',
        string='Line',
        required=True)
    product_id = fields.Many2one(
        'product.product', String="Product")
    workstation_id = fields.Many2one(
        'mdc.workstation',
        string='Workstation',
        required=True,
        domain=_get_workstation_id_domain)
    chkpoint_id = fields.Many2one(
        'mdc.chkpoint',
        string='Checkpoint',
        required=True,
        domain=_get_chkpoint_id_domain)
    shift_id = fields.Many2one(
        'mdc.shift',
        string='Shift',
        required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True)
    lot_id = fields.Many2one(
        'mdc.lot',
        string='MO',
        required=True)
    gross_weight = fields.Float(
        'Gross Weight',
        required=True)
    gross_weight_datetime = fields.Datetime(
        'Gross Weight Datetime',
        required=True,
        default=_default_date)
    clean_weight = fields.Float(
        'Clean Weight')
    clean_weight_datetime = fields.Datetime(
        'Clean Weight Datetime')
    w_uom_id = fields.Many2one(
        'product.uom',
        string='Weight UoM',
        required=True,
        domain=_get_w_uom_id_domain,
        default=_default_uom)
    filter_date = fields.Date(
        string="Date",
        compute="_compute_filter_date",
        store=True)

    @api.multi
    @api.depends('gross_weight_datetime')
    def _compute_filter_date(self):
        for record in self:
            record.filter_date = fields.Datetime.from_string(record.gross_weight_datetime).date()

    @api.onchange('chkpoint_id')
    def _retrieve_line_from_checkpoint(self):
        for data in self:
            data.line_id = self.chkpoint_id.line_id

    @api.onchange('workstation_id')
    def _retrieve_data_from_workstation(self):
        for data in self:
            data.employee_id = self.workstation_id.current_employee_id
            data.shift_id = self.workstation_id.shift_id

    @api.onchange('lot_id')
    def _retrieve_product_from_lot(self):
        for data in self:
            data.product_id = self.lot_id.product_id

    def from_cp_create(self, vals):
        '''
        Saves a checkpoint entry from some input data (Crumbs)
        '''
        # Data received:
        # - workstation
        # - employee
        # - lot
        # - shift

        chkpoint = self.env['mdc.chkpoint'].browse(vals['chkpoint_id'])

        # VALIDATIONS
        # wout_categ_id = self.env['mdc.wout_categ'].search([('code', '=', values['wout_categ_code'])])
        # if not wout_categ_id:
        #     raise UserError(_('WOUT categ code #%s not found') % values['wout_categ_code'])
        if not chkpoint:
            return {'error' : _('Checkpoint #%s not found') % vals['chkpoint_id']}
        if not chkpoint.scale_id:
            return {'error' : _("Scale not defined")}
        if not chkpoint.tare_id:
            return {'error' : _("Tare not defined")}
        # Get DataCrumb records
        dataCrumbRecords = self.env['mdc.data_crumbs'].search(
            [('employee_id','=', int(vals['employee'])),
             ('clean_weight_datetime','=', False)
            ])

        if dataCrumbRecords:
            return {'error' : _('Can`t create new data crumb for this employee, already exist one without finish (id #%s, lot #%s)') % (dataCrumbRecords.id, dataCrumbRecords.lot_id.name)}
        # Get weight
        try:
            weight_value, weight_uom_id, weight_stability = chkpoint.scale_id.get_weight()[0:3]
        except socket.timeout:
            return {'error' : _("Timed out on weighing scale")}

        if weight_stability == 'unstable':
            return {'error' : _('Unstable %.2f %s weight was read. Please stabilize container and try again') % (weight_value, weight_uom_id.name)}

        gross_weight = weight_value - chkpoint.tare_id.tare
        if gross_weight <=0:
            return {'error': _("Incorrect weight (%.2f) or tare (%.2f)") % (weight_value, chkpoint.tare_id.tare)}

        return self.create({
            'line_id': chkpoint.line_id.id,
            'workstation_id': vals['workstation'],
            'chkpoint_id': chkpoint.id,
            'shift_id': vals['shift'],
            'employee_id': vals['employee'],
            'lot_id': vals['lot'],
            'gross_weight': gross_weight,
            'gross_weight_datetime': fields.Datetime.now(),
            'w_uom_id': weight_uom_id.id,
            'product_id': vals['product_id']
        })

    def from_cp_update(self, vals):
        '''
        Updates a checkpoint entry from some input data (Crumbs)
        '''

        # Data received:
        # - workstation
        # - employee
        # - lot
        # - shift

        chkpoint = self.env['mdc.chkpoint'].browse(vals['chkpoint_id'])

        # VALIDATIONS
        # wout_categ_id = self.env['mdc.wout_categ'].search([('code', '=', values['wout_categ_code'])])
        # if not wout_categ_id:
        #     raise UserError(_('WOUT categ code #%s not found') % values['wout_categ_code'])
        if not chkpoint:
            return {'error' : _('Checkpoint #%s not found') % vals['chkpoint_id']}
        if not chkpoint.scale_id:
            return {'error' : _("Scale not defined")}
        if not chkpoint.tare_id:
            return {'error' : _("Tare not defined")}

        # Get DataCrumb record
        dataCrumb = self.env['mdc.data_crumbs'].search(
            [
                ('workstation_id','=', int(vals['workstation'])),
                ('employee_id','=', int(vals['employee'])),
                ('lot_id','=', int(vals['lot'])),
                ('shift_id','=', int(vals['shift'])),
                ('clean_weight_datetime','=', False)
            ], limit=1)
        if not dataCrumb:
            return {'error' : _('No open record found with this shift, lot and employee')}

        # Get weight
        try:
            weight_value, weight_uom_id, weight_stability = chkpoint.scale_id.get_weight()[0:3]
        except socket.timeout:
            return {'error' : _("Timed out on weighing scale")}

        if weight_stability == 'unstable':
            return {'error' : _('Unstable %.2f %s weight was read. Please stabilize container and try again') %
                (weight_value, weight_uom_id.name)}

        clean_weight = weight_value - chkpoint.tare_id.tare
        if clean_weight <=0:
            return {'error': _("Incorrect weight (%.2f) or tare (%.2f)") % (weight_value, chkpoint.tare_id.tare)}

        gross_weight = dataCrumb.gross_weight
        if clean_weight > gross_weight:
            return {'error': _("Incorrect weighing. The clean weight (%.2f) cannot be greater than the uncleaned weight (%.2f)") % (clean_weight, gross_weight)}

        dataCrumb.clean_weight = clean_weight
        dataCrumb.clean_weight_datetime = fields.Datetime.now()

        return {
            'clean_weight': clean_weight,
        }

    # @api.model
    # def create(self, vals):
    #     return super(DataCrumbs ,self).create(vals)
