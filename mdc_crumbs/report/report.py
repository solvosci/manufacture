# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _

class dataCrumbsReport(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_crumbs) in order to be filtered by dates and exported to Excel

    """
    _name = 'mdc.rpt_data_crumbs'
    _description = 'Report Data Crumbs CheckPoint'
    # _order = 'create_date asc'
    _auto = False

    #Table DataCrumb data
    create_date = fields.Date('Create Date', readonly=True)
    line_id = fields.Many2one('mdc.line', string="Line", readonly=True)
    workstation_id = fields.Many2one('mdc.workstation', string="Wokstation", readonly=True)
    chkpoint_id = fields.Many2one('mdc.chkpoint', string="CheckPoint", readonly=True)
    shift_id = fields.Char(readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True)
    lot_id = fields.Many2one('mdc.lot', string="Lot", readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    gross_weight = fields.Float('Gross Weight', readonly=True)
    gross_weight_datetime = fields.Datetime('Gross Weight DateTime', readonly=True)
    clean_weight = fields.Float('Clean Weight', readonly=True)
    clean_weight_datetime = fields.Datetime('Clean Weight DateTime', readonly=True)
    w_uom_id = fields.Many2one('product.uom', string="Weight unit of measure", readonly=True)
    employee_name = fields.Char(related="employee_id.name", readonly=True, string="Employee")
    lot_name = fields.Char(string="Lot", related="lot_id.name", readonly=True)
    line_name = fields.Char(string="Line", readonly=True, related='line_id.name')
                

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
        CREATE view %s as
                    SELECT * FROM mdc_data_crumbs
        """ % self._table)
