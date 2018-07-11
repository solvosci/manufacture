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
        row=header_row+1
        for obj in rpt_tracing:
            # ditect data from view database
            # TODO: Get real product-attribute name
            pr_std = self.env['product.product'].search([('id', '=', obj.product_id)])
            sheet.write(row, 0, obj.lot_name)
            sheet.write(row, 1, obj.employee_code)
            sheet.write(row, 2, obj.employee_name)
            sheet.write(row, 3, pr_std.name)
            sheet.write(row, 4, obj.shift_code)
            sheet.write(row, 5, obj.gross_weight)
            sheet.write(row, 6, obj.product_weight)
            sheet.write(row, 7, obj.sp1_weight)
            sheet.write(row, 8, obj.quality)
            sheet.write(row, 9, "TODO")

            # data formulation
            sheet.write_formula(row, 10, '=G' + str(row+1) + '/F' + str(row+1), f_percent)
            sheet.write_formula(row, 12, '=H' + str(row+1) + '/F' + str(row+1), f_percent)
            sheet.write_formula(row, 13, '=(G' + str(row + 1) + '+H' + str(row + 1) + ')/F' + str(row + 1), f_percent)

            row=row+1

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('B2')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)
