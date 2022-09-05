# -*- coding: utf-8 -*-
from odoo import models, _
from odoo.addons.mdc.report import report_xlsx
import base64
import tempfile
import datetime


def formats():
    return {
        **report_xlsx.formats()
    }


class dataCrumbsReportxlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_data_crumbs'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, data_crumbs):
        report_name = "rpt_data_crumbs"
        sheet = workbook.add_worksheet("Data crumbs records")

        # General sheet style
        sheet.set_landscape()
        sheet.repeat_rows(0, 5)
        sheet.hide_gridlines(3)

        # get Formats Dictionary from standard function formats
        f_cells = formats()
        f_title = workbook.add_format(f_cells["title"])
        f_header = workbook.add_format(f_cells["header"])
        f_header_ind = workbook.add_format(f_cells["header_ind"])
        f_filter = workbook.add_format(f_cells["filter_date"])
        f_date_time = workbook.add_format({'text_wrap': True, 'num_format': 'yyyy-mm-dd hh:mm:ss'})
        f_percent = workbook.add_format(f_cells["percent"])
        f_data = workbook.add_format(f_cells["data"])
        f_data2d = workbook.add_format(f_cells["data2d"])
        f_footer = workbook.add_format(f_cells["footer"])
        f_footer_perc = workbook.add_format(f_cells["footer_perc"])

        # Set columns widths
        sheet.set_column('A:A', 17)
        sheet.set_column('B:B', 8)
        sheet.set_column('C:N', 15)
        sheet.set_column('E:E', 25)
        sheet.set_column('F:F', 40)
        sheet.set_column('G:G', 18)
        sheet.set_column('H:H', 12)
        sheet.set_column('I:I', 18)
        sheet.set_column('J:J', 12)
        sheet.set_column('K:N', 15)

        # write logo
        logo_file_name = False
        binary_logo = self.env['res.company'].sudo().search([]).logo_web
        if binary_logo:
            fp = tempfile.NamedTemporaryFile(delete=False)
            fp.write(bytes(base64.b64decode(binary_logo)))
            fp.close()
            logo_file_name = fp.name
        else:
            # TODO enhance default logo path recovery
            logo_file_name = "../addons/manufacture/mdc/report/logo.png"

        sheet.insert_image('A1', logo_file_name, {
            'x_offset': 18, 'y_offset': 18, 'x_scale': 0.9, 'y_scale': 0.5})

        # # write Title
        sheet.write(1, 5, _("DATA CRUMBS REPORT"), f_title)
        # # # write current date
        sheet.write(2, 5, datetime.datetime.now(), f_filter)

        header_row = 5
        header_row_str = str(header_row + 1)
        # # # write column header ----------------------------------------
        sheet.write('A' + header_row_str, _("Line"), f_header)
        sheet.write('B' + header_row_str, _("Shift"), f_header)
        sheet.write('C' + header_row_str, _("Lot"), f_header)
        sheet.write('D' + header_row_str, _("Product"), f_header)
        sheet.write('E' + header_row_str, _("Cleaning"), f_header)
        sheet.write('F' + header_row_str, _("Employee"), f_header)
        sheet.write('G' + header_row_str, _("Gross Weight Datetime"), f_header)
        sheet.write('H' + header_row_str, _("Gross Weight"), f_header)
        sheet.write('I' + header_row_str, _("Clean Weight Datetime"), f_header)
        sheet.write('J' + header_row_str, _("Clean Weight"), f_header)
        sheet.write('K' + header_row_str, _("MO (min/Kg)"), f_header)
        sheet.write('L' + header_row_str, _("RD (%)"), f_header)
        sheet.write('M' + header_row_str, _("STD RD"), f_header)
        sheet.write('N' + header_row_str, _("IND RD"), f_header)

        # -------------------------------------------------------


        # write data rows
        row = header_row

        # we order the result in case changed the order in the view
        data_crumbs = data_crumbs.sorted("shift_id")

        for obj in data_crumbs:

            row = row + 1

            # direct data from view database
            sheet.write(row, 0, obj.line_name, f_data)
            sheet.write(row, 1, obj.shift_id, f_data)
            sheet.write(row, 2, obj.lot_name, f_data)
            row_product_id = obj.product_id
            if not row_product_id:
                row_product_id = obj.lot_id.product_id
            sheet.write(row, 3, row_product_id.name, f_data)
            variable_attributes = row_product_id.attribute_line_ids.mapped('attribute_id')
            variant = row_product_id.attribute_value_ids._variant_name(variable_attributes)
            sheet.write(row, 4, variant, f_data)
            sheet.write(row, 5, obj.employee_name, f_data)
            sheet.write(row, 6, obj.gross_weight_datetime, f_date_time)
            sheet.write(row, 7, obj.gross_weight, f_data2d)
            if(obj.clean_weight_datetime != False):
                sheet.write(row, 8, obj.clean_weight_datetime, f_date_time)
            sheet.write(row, 9, obj.clean_weight, f_data2d)
            sheet.write_formula(row, 10, '=IF(OR(H' + str(row + 1) + '=0, I' + str(row + 1) + '=""),"",' + '((I' + str(row + 1) + '-G' + str(row + 1) + ')*1440)/H' + str(row + 1) + ')',
                f_data2d)
            sheet.write_formula(row, 11, '=IF(J' + str(row + 1) + '=0,"",' + '(J' + str(row + 1) + '/H' + str(row + 1) + ')*100)',
                f_data2d)
            sheet.write(row, 12, obj.lot_id.std_yield_sp1, f_data2d)
            sheet.write_formula(row, 13, '=IF(OR(M' + str(row + 1) + '=0, L' + str(row + 1) + '=""),"",' + 'L' + str(row + 1) + '/M' + str(row + 1) + ')',
                f_percent)


        

            # # Filters: ----------------------------------------
            # # min a max date
            # if wstart_date is False or wstart_date > obj.create_date:
            #     wstart_date = obj.create_date
            # if wend_date is False or wend_date < obj.create_date:
            #     wend_date = obj.create_date
            # # shift
            # if wshift_filter == '':
            #     wshift_filter = obj.shift_code
            # # line
            # if wline_filter == '':
            #     wline_filter = obj.line_code
            # # ------------------------------------------------

            # # shift Filter
            # if wshift_filter != obj.shift_code:
            #     wshift_filter_uniq = False
            # # Line Filter
            # if wline_filter != obj.line_code:
            #     wline_filter_uniq = False




            # # direct data from view database
            # sheet.write(row, 0, obj.employee_code, f_data)
            # sheet.write(row, 1, obj.employee_name, f_data)

            
            # res_wind_backs_weight = 0
            # res_wind_mo_weight = 0
            # res_wind_crumbs_weight = 0
            # res_wind_quality_weight = 0
            # res_wind_cleaning_weight = 0

            # # columns with grouped data - indicators
            # sheet.write(row, 2, res_wind_backs_weight, f_percent)
            # sheet.write(row, 3, res_wind_mo_weight, f_percent)
            # sheet.write(row, 4, res_wind_crumbs_weight, f_percent)
            # sheet.write(row, 5, res_wind_quality_weight, f_percent)
            # sheet.write(row, 6, res_wind_cleaning_weight, f_percent)

            # # Final Footer Row ------------------------------------------
            # for numcol in range(0, 3):
            #     sheet.write(row + 1, numcol, '', f_footer)
            #sheet.write_formula(row + 1, 8, '=SUM(I' + str(header_row + 1) + ':I' + str(row + 1) + ')', f_footer)

            # # # formulation columns - indicators
            # # sheet.write_formula(row + 1, 8, '=SUM(I' + str(header_row + 1) + ':I' + str(row + 1) + ')', f_footer)
            # # sheet.write_formula(row + 1, 2,
            # #                     '=IF(I' + str(row + 2) + '= 0, 0 , SUMPRODUCT(C' + str(header_row + 1) + ':C' + str(
            # #                         row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ') / I' + str(
            # #                         row + 2) + ')', f_footer_perc)
            # # sheet.write_formula(row + 1, 3,
            # #                     '=IF(I' + str(row + 2) + '= 0, 0 , SUMPRODUCT(D' + str(header_row + 1) + ':D' + str(
            # #                         row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ') / I' + str(
            # #                         row + 2) + ')', f_footer_perc)
            # # sheet.write_formula(row + 1, 4,
            # #                     '=IF(I' + str(row + 2) + '= 0, 0 , SUMPRODUCT(E' + str(header_row + 1) + ':E' + str(
            # #                         row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ') / I' + str(
            # #                         row + 2) + ')', f_footer_perc)
            # # sheet.write_formula(row + 1, 5,
            # #                     '=IF(I' + str(row + 2) + '= 0, 0 , SUMPRODUCT(F' + str(header_row + 1) + ':F' + str(
            # #                         row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ') / I' + str(
            # #                         row + 2) + ')', f_footer_perc)
            # # sheet.write_formula(row + 1, 6,
            # #                     '=IF(I' + str(row + 2) + '= 0, 0 , SUMPRODUCT(G' + str(header_row + 1) + ':G' + str(
            # #                         row + 1) + ', I' + str(header_row + 1) + ':I' + str(row + 1) + ') / I' + str(
            # #                         row + 2) + ')', f_footer_perc)

        # # Final Presentation
        # # Select the cells back to image & zoom presentation & split & freeze_panes
        # sheet.set_selection('A6')
        # sheet.set_zoom(80)
        # # sheet.split_panes(60,0,5,0)
        sheet.set_selection('A6')
        sheet.set_zoom(80)
