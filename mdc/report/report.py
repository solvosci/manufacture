# -*- coding: utf-8 -*-

from odoo import models, fields, tools, _

class RptTracing(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_win & data_wout) in order to be filtered by dates and exported to Excel
    """
    _name = 'mdc.rpt_tracing'
    _description = 'Tracing Report'
    _order = 'create_date'
    _auto = False

    create_date = fields.Date('Date', readonly=True)
    lot_name = fields.Char('Lot', readonly=True)
    employee_code = fields.Char('Employee Code', readonly=True)
    employee_name = fields.Char('Employee Name', readonly=True)
    product_id = fields.Integer('Product Id', readonly=True)
    shift_code = fields.Char('Shift Code', readonly=True)
    gross_weight = fields.Float('Gross', readonly=True)
    product_weight = fields.Float('Backs', readonly=True)
    sp1_weight = fields.Float('Crumbs', readonly=True)
    quality = fields.Char('Quality', readonly=True)

    def _select(self):
        select_str = """
             SELECT
                    MIN(wout.id) as id,
                    date(wout.create_datetime) as create_date,
                    lot.name as lot_name,
                    emp.employee_code as employee_code,
                    emp.name as employee_name,
                    lot.product_id as product_id,
                    shift.shift_code as shift_code,
                    sum(wout.gross_weight) as gross_weight,
                    sum(case when woutcat.code='P' then wout.weight-wout.tare else 0 end) as product_weight,
                    sum(case when woutcat.code='SP1' then wout.weight-wout.tare else 0 end) as sp1_weight,
                    AVG(CAST(qlty.name AS INTEGER)) as quality
        """
        return select_str

    def _group_by(self):
        group_by_str = """
            GROUP BY 
                date(wout.create_datetime),
                lot.name,
                emp.employee_code,
                emp.name,
                lot.product_id,
                shift.shift_code
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as
              %s
              FROM mdc_data_wout wout
              LEFT JOIN mdc_lot lot ON lot.id=wout.lot_id
              LEFT JOIN hr_employee emp ON emp.id=wout.employee_id
              LEFT JOIN mdc_shift shift ON shift.id=wout.shift_id
              LEFT JOIN mdc_wout_categ woutcat ON woutcat.id=wout.wout_categ_id 
              LEFT JOIN mdc_quality qlty ON qlty.id=wout.quality_id
              WHERE 1=1
              %s
        """ % (self._table, self._select(), self._group_by()))

