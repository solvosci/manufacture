# -*- coding: utf-8 -*-
from addons.product.models.product_attribute import ProductAttributevalue
from odoo import models, _
import os

def formats():
    # Python dictionary with cells formats and styles for XLSX reports
    dic_formats={}
    dic_formats["title"] = {'bold': True, 'size': 30}
    dic_formats["filter"] = {'bold': True,
                             'font_color': '#004080',
                             'size': 16}
    dic_formats["header"] = {'bold': True,
                             'font_color': '#004080',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
                             'align': 'center',
                             'size': 12}
    dic_formats["data"] = {}
    dic_formats["percent"] = {'num_format': '0.00%'}
    return dic_formats



class ReportRptTracingXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_tracing'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, rpt_tracing):
        report_name = "rpt_tracing"
        sheet = workbook.add_worksheet("Tracing Report")

        # General sheet style
        sheet.set_landscape()
        sheet.repeat_rows(0,5)
        sheet.hide_gridlines(3)

        # get Formats Dictionary from standard function formats
        f_cells = formats()
        f_title = workbook.add_format(f_cells["title"])
        f_header = workbook.add_format(f_cells ["header"])
        f_filter = workbook.add_format(f_cells["filter"])
        f_percent = workbook.add_format(f_cells ["percent"])

        # Set columns widths
        sheet.set_column('A:L', 12)
        sheet.set_column('C:D', 40) # Employee name and STD name columns

        # write logo
        # TODO: get logo from Company
        # path = os.getcwd().
        logo = "../addons/manufacture/mdc/report/logo.png"
        sheet.insert_image('A1', logo, {'x_offset': 18, 'y_offset': 18, 'x_scale': 0.9, 'y_scale': 0.5})

        # write Title
        sheet.write(1, 2, _("TRACE PRODUCTION REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row=5
        # write column header
        sheet.write(header_row, 0, _("Lot"), f_header)
        sheet.write(header_row, 1, _("Employee Code"), f_header)
        sheet.write(header_row, 2, _("Employee Name"), f_header)
        sheet.write(header_row, 3, _("STD"), f_header)
        sheet.write(header_row, 4, _("Shift"), f_header)
        sheet.write(header_row, 5, _("Gross"), f_header)
        sheet.write(header_row, 6, _("Backs"), f_header)
        sheet.write(header_row, 7, _("Crumbs"), f_header)
        sheet.write(header_row, 8, _("Quality"), f_header)
        sheet.write(header_row, 9, _("Time"), f_header)
        sheet.write(header_row, 10, _("% Backs"), f_header)
        sheet.write(header_row, 11, _("STD Back"), f_header)
        sheet.write(header_row, 12, _("% Crumbs"), f_header)
        sheet.write(header_row, 13, _("% Total Yield"), f_header)
        sheet.write(header_row, 14, _("STD Crum"), f_header)
        sheet.write(header_row, 15, _("Workforce"), f_header)
        sheet.write(header_row, 16, _("STD Workforce"), f_header)

        # write data rows
        row=header_row
        wlot_name = ''
        wemployee_code = ''
        wshift_code = ''
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wquality = 0
        wtotal_hours = 0
        wnumreg = 0
        wstart_date = False
        wend_date = False
        for obj in rpt_tracing:

            #min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date

            if (wlot_name != obj.lot_name) or (wemployee_code != obj.employee_code) or (wshift_code != obj.shift_code):
                row = row + 1

                # direct data from view database
                product_name = obj.product_id.name_get()[0][1]
                sheet.write(row, 0, obj.lot_name)
                sheet.write(row, 1, obj.employee_code)
                sheet.write(row, 2, obj.employee_name)
                sheet.write(row, 3, product_name)
                sheet.write(row, 4, obj.shift_code)
                # std columns
                sheet.write(row, 11, obj.std_yield_product)
                sheet.write(row, 14, obj.std_yield_sp1)
                sheet.write(row, 16, obj.std_speed)
                # formulation columns
                sheet.write_formula(row, 10, '=G' + str(row+1) + '/F' + str(row+1), f_percent)
                sheet.write_formula(row, 12, '=H' + str(row+1) + '/F' + str(row+1), f_percent)
                sheet.write_formula(row, 13, '=(G' + str(row + 1) + '+H' + str(row + 1) + ')/F' + str(row + 1), f_percent)

                wgross_weight = 0
                wproduct_weight = 0
                wsp1_weight = 0
                wquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight += obj.gross_weight
            wproduct_weight += obj.product_weight
            wsp1_weight += obj.sp1_weight
            wquality += obj.quality
            wtotal_hours += obj.total_hours
            wnumreg += 1

            #columns with grouped data
            sheet.write(row, 5, wgross_weight)
            sheet.write(row, 6, wproduct_weight)
            sheet.write(row, 7, wsp1_weight)
            sheet.write(row, 8, wquality/wnumreg)
            sheet.write(row, 9, wtotal_hours)

            wlot_name = obj.lot_name
            wemployee_code = obj.employee_code
            wshift_code = obj.shift_code

        # write Filter
        datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
        if wstart_date == wend_date:
            datefilter = _("Date: #%s") % wstart_date
        sheet.write(2, 2, datefilter, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('B2')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)
