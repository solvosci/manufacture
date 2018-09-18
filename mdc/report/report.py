# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _

class RptTracing(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_win & data_wout) in order to be filtered by dates and exported to Excel
    """
    _name = 'mdc.rpt_tracing'
    _description = 'Tracing Report'
    _order = 'lot_name asc, employee_code asc, shift_code asc'
    _auto = False

    create_date = fields.Date('Date', readonly=True)
    lot_name = fields.Char('Lot', readonly=True)
    employee_code = fields.Char('Employee Code', readonly=True)
    employee_name = fields.Char('Employee Name', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    shift_code = fields.Char('Shift Code', readonly=True)
    gross_weight = fields.Float('Gross', readonly=True, group_operator='sum')
    product_weight = fields.Float('Backs', readonly=True, group_operator='sum')
    sp1_weight = fields.Float('Crumbs', readonly=True, group_operator='sum')
    quality = fields.Float('Quality', readonly=True, group_operator='avg')
    total_hours = fields.Float('Total Hours', readonly=True, group_operator='sum')
    # TODO readonly=True
    std_yield_product = fields.Float('Std Yield Product')
    std_speed = fields.Float('Std Speed')
    std_yield_sp1 = fields.Float('Std Yield Subproduct 1')

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as 
                SELECT lotdata.id, lotdata.create_date, lotdata.lot_name, lotdata.product_id, 
                    lotdata.employee_code, lotdata.employee_name, lotdata.shift_code, 
                    lotdata.gross_weight, lotdata.product_weight, lotdata.sp1_weight, lotdata.quality, 
                    lotemp.total_hours, 
                    std.std_yield_product, std.std_speed, std.std_yield_sp1 
                    FROM (
                        SELECT
                            MIN(wout.id) as id,
                            date(wout.create_datetime) as create_date,
                            lot.id as lot_id, lot.name as lot_name,lot.product_id as product_id,
                            emp.id as employee_id, emp.employee_code as employee_code,emp.name as employee_name,
                            shift.id shift_id, shift.shift_code as shift_code,
                            sum(wout.gross_weight) as gross_weight,
                            sum(case when woutcat.code='P' then wout.weight-wout.tare else 0 end) as product_weight,
                            sum(case when woutcat.code='SP1' then wout.weight-wout.tare else 0 end) as sp1_weight,
                            AVG(qlty.code) as quality
                        FROM mdc_data_wout wout
                            LEFT JOIN mdc_lot lot ON lot.id=wout.lot_id
                            LEFT JOIN hr_employee emp ON emp.id=wout.employee_id
                            LEFT JOIN mdc_shift shift ON shift.id=wout.shift_id
                            LEFT JOIN mdc_wout_categ woutcat ON woutcat.id=wout.wout_categ_id 
                            LEFT JOIN mdc_quality qlty ON qlty.id=wout.quality_id
                        WHERE 1=1
                        GROUP BY 
                            date(wout.create_datetime),
                            lot.id, lot.name, lot.product_id,
                            emp.id, emp.employee_code, emp.name,
                            shift.id, shift.shift_code
                    ) lotdata
                    LEFT JOIN (SELECT 
                            date(ws.start_datetime) as start_date,
                            ws.lot_id, ws.employee_id, ws.shift_id, 
                            sum(ws.total_hours) as total_hours 
                        FROM mdc_worksheet ws
                        WHERE 1=1
                        GROUP BY date(ws.start_datetime),
                            ws.lot_id, ws.employee_id, ws.shift_id
                    ) lotemp ON lotemp.start_date=lotdata.create_date 
                            and lotemp.lot_id=lotdata.lot_id and lotemp.employee_id=lotdata.employee_id 
                            and lotemp.shift_id=lotdata.shift_id 
                    LEFT JOIN mdc_std std on std.product_id = lotdata.product_id     
                
        """ % self._table)


    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
               orderby=False, lazy=True):
        res = super(RptTracing, self).read_group(domain, fields, groupby,
             offset=offset, limit=limit, orderby=orderby, lazy=lazy)

        # TODO if we need to customize some group operators, edit here
        # http://danielrodriguez.esy.es/blog/sumatory-in-group/

        return res


class RptManufacturing(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_win & data_wout) in order to be filtered by dates and exported to Excel
    """
    _name = 'mdc.rpt_manufacturing'
    _description = 'Manufacturing Report'
    _order = 'lot_name asc, employee_code asc, shift_code asc, workstation_name asc'
    _auto = False

    create_date = fields.Date('Date', readonly=True)
    lot_name = fields.Char('Lot', readonly=True)
    employee_code = fields.Char('Employee Code', readonly=True)
    employee_name = fields.Char('Employee Name', readonly=True)
    contract_name = fields.Char('Contract Name', readonly=True)
    workstation_name = fields.Char('Workstation Name', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    shift_code = fields.Char('Shift Code', readonly=True)
    gross_weight = fields.Float('Gross', readonly=True, group_operator='sum')
    product_weight = fields.Float('Backs', readonly=True, group_operator='sum')
    sp1_weight = fields.Float('Crumbs', readonly=True, group_operator='sum')
    quality = fields.Float('Quality', readonly=True, group_operator='avg')
    total_hours = fields.Float('Total Hours', readonly=True, group_operator='sum')
    # TODO readonly=True
    std_yield_product = fields.Float('Std Yield Product')
    std_speed = fields.Float('Std Speed')
    std_yield_sp1 = fields.Float('Std Yield Subproduct 1')

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as 
                SELECT lotdata.id, lotdata.create_date, lotdata.lot_name, lotdata.product_id, 
                    lotdata.employee_code, lotdata.employee_name, lotdata.contract_name, lotdata.shift_code, 
                    lotdata.gross_weight, lotdata.product_weight, lotdata.sp1_weight, lotdata.quality, 
                    lotdata.workstation_name, 
                    lotemp.total_hours, 
                    std.std_yield_product, std.std_speed, std.std_yield_sp1 
                    FROM (
                        SELECT
                            MIN(wout.id) as id,
                            date(wout.create_datetime) as create_date,
                            lot.id as lot_id, lot.name as lot_name,lot.product_id as product_id,
                            emp.id as employee_id, emp.employee_code as employee_code,emp.name as employee_name,
                            contr.name as contract_name,
                            wst.name as workstation_name,
                            shift.id shift_id, shift.shift_code as shift_code,
                            sum(wout.gross_weight) as gross_weight,
                            sum(case when woutcat.code='P' then wout.weight-wout.tare else 0 end) as product_weight,
                            sum(case when woutcat.code='SP1' then wout.weight-wout.tare else 0 end) as sp1_weight,
                            AVG(qlty.code) as quality
                        FROM mdc_data_wout wout
                            LEFT JOIN mdc_lot lot ON lot.id=wout.lot_id
                            LEFT JOIN hr_employee emp ON emp.id=wout.employee_id
                            LEFT JOIN hr_contract_type contr ON contr.id=emp.contract_type_id
                            LEFT JOIN mdc_shift shift ON shift.id=wout.shift_id
                            LEFT JOIN mdc_wout_categ woutcat ON woutcat.id=wout.wout_categ_id 
                            LEFT JOIN mdc_quality qlty ON qlty.id=wout.quality_id
                            LEFT JOIN mdc_workstation wst ON wst.id=wout.workstation_id
                        WHERE 1=1
                        GROUP BY 
                            date(wout.create_datetime),
                            lot.id, lot.name, lot.product_id,
                            emp.id, emp.employee_code, emp.name,
                            contr.name,
                            wst.name,
                            shift.id, shift.shift_code
                    ) lotdata
                    LEFT JOIN (SELECT 
                            date(ws.start_datetime) as start_date,
                            ws.lot_id, ws.employee_id, ws.shift_id, 
                            sum(ws.total_hours) as total_hours 
                        FROM mdc_worksheet ws
                        WHERE 1=1
                        GROUP BY date(ws.start_datetime),
                            ws.lot_id, ws.employee_id, ws.shift_id
                    ) lotemp ON lotemp.start_date=lotdata.create_date 
                            and lotemp.lot_id=lotdata.lot_id and lotemp.employee_id=lotdata.employee_id 
                            and lotemp.shift_id=lotdata.shift_id 
                    LEFT JOIN mdc_std std on std.product_id = lotdata.product_id     

        """ % self._table)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(RptManufacturing, self).read_group(domain, fields, groupby,
                                                 offset=offset, limit=limit, orderby=orderby, lazy=lazy)

        # TODO if we need to customize some group operators, edit here
        # http://danielrodriguez.esy.es/blog/sumatory-in-group/

        return res

