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
    client_name = fields.Char('Client', readonly=True)
    shift_code = fields.Char('Shift Code', readonly=True)
    gross_weight = fields.Float('Gross', readonly=True, group_operator='sum')
    product_weight = fields.Float('Backs', readonly=True, group_operator='sum')
    sp1_weight = fields.Float('Crumbs', readonly=True, group_operator='sum')
    quality = fields.Float('Quality', readonly=True)
    total_hours = fields.Float('Total Hours', readonly=True, group_operator='sum')
    # TODO readonly=True
    std_yield_product = fields.Float('Std Yield Product')
    std_speed = fields.Float('Std Speed')
    std_yield_sp1 = fields.Float('Std Yield Subproduct 1')

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as 
                SELECT lotdata.id, lotdata.create_date, lotdata.lot_name, lotdata.product_id, cli.name as client_name,
                    lotdata.employee_code, lotdata.employee_name, lotdata.shift_code, 
                    lotdata.gross_weight, lotdata.product_weight, lotdata.sp1_weight, 
                    lotdata.quality_weight/lotdata.product_weight as quality, 
                    lotemp.total_hours, 
                    std.std_yield_product, std.std_speed, std.std_yield_sp1 
                    FROM (
                        SELECT
                            MIN(wout.id) as id,
                            date(wout.create_datetime) as create_date,
                            lot.id as lot_id, lot.name as lot_name, lot.product_id as product_id, lot.partner_id as partner_id,
                            emp.id as employee_id, emp.employee_code as employee_code,emp.name as employee_name,
                            shift.id shift_id, shift.shift_code as shift_code,
                            sum(wout.gross_weight) as gross_weight,
                            sum(case when woutcat.code='P' then wout.weight-wout.tare else 0 end) as product_weight,
                            sum(case when woutcat.code='SP1' then wout.weight-wout.tare else 0 end) as sp1_weight,
                            sum(case when woutcat.code='P' then qlty.code * (wout.weight-wout.tare) else 0 end) as quality_weight
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
                    LEFT JOIN res_partner cli on cli.id = lotdata.partner_id 
                    LEFT JOIN mdc_std std on std.product_id = lotdata.product_id     
                
        """ % self._table)

    # --------------- Calculate Grouped Values with Weighted average or complicated dropued formulas
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
               orderby=False, lazy=True):
        res = super(RptTracing, self).read_group(domain, fields, groupby,
             offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'quality' in fields:
            for line in res:
                if '__domain' in line:
                    quality_weight = 0
                    lines = self.search(line['__domain'])
                    for line_item in lines:
                        quality_weight += line_item.quality * line_item.product_weight
                    line['quality'] = quality_weight / line['product_weight']
        return res


class RptManufacturing(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_win & data_wout) in order to be filtered by dates and exported to Excel
    """
    _name = 'mdc.rpt_manufacturing'
    _description = 'Manufacturing Report'
    _order = 'lot_name asc, workstation_name asc, employee_code asc, shift_code asc'
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
    quality = fields.Float('Quality', readonly=True)
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
                    lotdata.gross_weight, lotdata.product_weight, lotdata.sp1_weight,
                    lotdata.quality_weight/lotdata.product_weight as quality, 
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
                            sum(case when woutcat.code='P' then qlty.code * (wout.weight-wout.tare) else 0 end) as quality_weight
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

    # --------------- Calculate Grouped Values with Weighted average or complicated dropued formulas
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(RptManufacturing, self).read_group(domain, fields, groupby,
                                                 offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'quality' in fields:
            for line in res:
                if '__domain' in line:
                    quality_weight = 0
                    lines = self.search(line['__domain'])
                    for line_item in lines:
                        quality_weight += line_item.quality * line_item.product_weight
                    line['quality'] = quality_weight / line['product_weight']
        return res


class RptIndicators(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_win & data_wout) in order to be filtered by dates and exported to Excel
    """
    _name = 'mdc.rpt_indicators'
    _description = 'Indicators Report'
    _order = 'shift_code asc, employee_code asc'
    _auto = False

    create_date = fields.Date('Date', readonly=True)
    lot_name = fields.Char('Lot', readonly=True)
    employee_code = fields.Char('Employee Code', readonly=True)
    employee_name = fields.Char('Employee Name', readonly=True)
    shift_code = fields.Char('Shift Code', readonly=True)
    gross_weight = fields.Float('Gross', readonly=True, group_operator='sum')
    product_weight = fields.Float('Backs', readonly=True, group_operator='sum')
    sp1_weight = fields.Float('Crumbs', readonly=True, group_operator='sum')
    quality = fields.Float('Quality', readonly=True)
    total_hours = fields.Float('Total Hours', readonly=True, group_operator='sum')
    # TODO readonly=True
    std_yield_product = fields.Float('Std Yield Product')
    std_speed = fields.Float('Std Speed')
    std_yield_sp1 = fields.Float('Std Yield Subproduct 1')
    ind_backs = fields.Float('IND Backs', readonly=True, group_operator='avg')
    ind_mo = fields.Float('IND MO', readonly=True, group_operator='avg')
    ind_crumbs = fields.Float('IND Crumbs', readonly=True, group_operator='avg')
    ind_quality = fields.Float('IND Quality', readonly=True, group_operator='avg')
    ind_cleaning = fields.Float('IND Cleaning', readonly=True, group_operator='avg')

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as 
                SELECT lotdata.id, lotdata.create_date, lotdata.lot_name,  
                    lotdata.employee_code, lotdata.employee_name, lotdata.shift_code, 
                    lotdata.gross_weight, lotdata.product_weight, lotdata.sp1_weight,
                    lotdata.quality_weight/lotdata.product_weight as quality,
                    lotemp.total_hours, 
                    std.std_yield_product, std.std_speed, std.std_yield_sp1, 
                    case when coalesce(std.std_yield_product,0) = 0 then 0 else (lotdata.product_weight / lotdata.gross_weight) / std.std_yield_product/ 1.15 end as ind_backs,
                    case when coalesce(std.std_speed,0) = 0 then 0 else (lotemp.total_hours * 60 / lotdata.gross_weight) / std.std_speed / 1.15 end as ind_mo,
                    case when coalesce(lotdata.sp1_weight,0) =0 then 0 else std.std_yield_sp1 / (lotdata.sp1_weight / lotdata.gross_weight) / 1.15 end as ind_crumbs,
                    lotdata.quality_weight / lotdata.product_weight as ind_quality,
                    case when coalesce(std.std_yield_product,0)*coalesce(std.std_speed,0) = 0 then 0 else
                    (0.6 *  ((lotdata.product_weight / lotdata.gross_weight) / std.std_yield_product/ 1.15)) 
                    + (0.3 * ((lotemp.total_hours * 60 / lotdata.gross_weight) / std.std_speed / 1.15)) 
                    + (0.1 * (lotdata.quality_weight / lotdata.product_weight)) end as ind_cleaning 
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
                            sum(case when woutcat.code='P' then qlty.code * (wout.weight-wout.tare) else 0 end) as quality_weight
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

    # --------------- Calculate Grouped Values with Weighted average or complicated dropued formulas
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(RptIndicators, self).read_group(domain, fields, groupby,
                                                 offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'ind_quality' in fields:
            for line in res:
                if '__domain' in line:
                    ind_quality_weight = 0
                    total_weight = 0
                    lines = self.search(line['__domain'])
                    for line_item in lines:
                        ind_quality_weight += line_item.quality * line_item.product_weight
                        total_weight += line_item.product_weight
                    line['ind_quality'] = ind_quality_weight / total_weight
        return res


class RptCumulative(models.Model):
    """
    View-mode model that ists data captured at checkpoints (data_win & data_wout) in order to be filtered by dates and exported to Excel
    """
    _name = 'mdc.rpt_cumulative'
    _description = 'Cumulative Report'
    _order = 'shift_code asc, employee_code asc'
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
        res = super(RptCumulative, self).read_group(domain, fields, groupby,
                                                 offset=offset, limit=limit, orderby=orderby, lazy=lazy)

        # TODO if we need to customize some group operators, edit here
        # http://danielrodriguez.esy.es/blog/sumatory-in-group/

        return res