# -*- coding: utf-8 -*-
from addons.product.models.product_attribute import ProductAttributevalue
from odoo import models, _
import base64
import tempfile

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
    dic_formats["footer"] = {'bold': True,
                             'font_color': '#003060',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
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
        f_data = workbook.add_format(f_cells ["data"])

        # Set columns widths
        sheet.set_column('A:W', 16)
        sheet.set_column('C:D', 40) # Employee name and STD name columns

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

        # write Title
        sheet.write(1, 2, _("TRACING REPORT"), f_title)

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
        sheet.write(header_row, 14, _("STD Crumbs"), f_header)
        sheet.write(header_row, 15, _("Workforce"), f_header)
        sheet.write(header_row, 16, _("STD Workforce"), f_header)
        sheet.write(header_row, 17, _("IND Backs"), f_header)
        sheet.write(header_row, 18, _("IND Workforce"), f_header)
        sheet.write(header_row, 19, _("IND Crumbs"), f_header)
        sheet.write(header_row, 20, _("IND Quality"), f_header)
        sheet.write(header_row, 21, _("IND Cleaning"), f_header)

        # TODO alternate dict list with almost grouped data (still problems with product and date)
        """
        grouped_rpt_tracing = self.env['mdc.rpt_tracing'].read_group(
            domain=[('id', 'in', rpt_tracing.ids)],
            fields=['lot_name', 'employee_code', 'product_id', 'shift_code',
                    'std_yield_product', 'std_yield_sp1', 'std_speed', 'gross_weight', 'product_weight',
                    'sp1_weight', 'quality', 'total_hours'],
            groupby=['lot_name', 'employee_code', 'shift_code'],
            lazy=False)
        for trace in grouped_rpt_tracing:
            pass
        """

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
                # sheet.write(row, 15, obj.std_speed)
                sheet.write(row, 16, obj.std_speed)
                # formulation columns
                sheet.write_formula(row, 10, '=G' + str(row+1) + '/F' + str(row+1), f_percent)
                sheet.write_formula(row, 12, '=H' + str(row+1) + '/F' + str(row+1), f_percent)
                sheet.write_formula(row, 13, '=(G' + str(row + 1) + '+H' + str(row + 1) + ')/F' + str(row + 1), f_percent)
                # Ind columns
                sheet.write_formula(row, 17, '=IF(L' + str(row + 1) + '= 0, 0, (K' + str(row + 1) + '/L' + str(row + 1) + ') * 100)', f_data)
                sheet.write_formula(row, 18, '=IF(Q' + str(row + 1) + '= 0, 0, (P' + str(row + 1) + '/Q' + str(row + 1) + ') * 100)', f_data)
                sheet.write_formula(row, 19, '=IF(O' + str(row + 1) + '= 0, 0, (M' + str(row + 1) + '/O' + str(row + 1) + ') * 100)', f_data)
                sheet.write(row, 20, obj.std_yield_sp1)
                sheet.write(row, 21, obj.std_speed)

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


class ReportRptManufacturingXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_manufacturing'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, rpt_manufacturing):
        report_name = "rpt_manufacturing"
        sheet = workbook.add_worksheet("Manufacturing Report")

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
        f_data = workbook.add_format(f_cells ["data"])
        f_footer = workbook.add_format(f_cells["footer"])

        # Set columns widths
        sheet.set_column('A:W', 16)
        sheet.set_column('C:C', 40) # Employee name

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

        # write Title
        sheet.write(1, 2, _("MANUFACTURING REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row=5
        # write column header
        sheet.write(header_row, 0, _("Workstation"), f_header)
        sheet.write(header_row, 1, _("Employee Code"), f_header)
        sheet.write(header_row, 2, _("Employee Name"), f_header)
        sheet.write(header_row, 3, _("Contract"), f_header)
        sheet.write(header_row, 4, _("Lot"), f_header)
        sheet.write(header_row, 5, _("Gross"), f_header)
        sheet.write(header_row, 6, _("Backs"), f_header)
        sheet.write(header_row, 7, _("Crumbs"), f_header)
        sheet.write(header_row, 8, _("Quality"), f_header)
        sheet.write(header_row, 9, _("Time"), f_header)
        sheet.write(header_row, 10, _("% Backs"), f_header)
        sheet.write(header_row, 11, _("STD Back"), f_header)
        sheet.write(header_row, 12, _("% Crumbs"), f_header)
        sheet.write(header_row, 13, _("% Total Yield"), f_header)
        sheet.write(header_row, 14, _("STD Crumbs"), f_header)
        sheet.write(header_row, 15, _("Workforce"), f_header)
        sheet.write(header_row, 16, _("STD Workforce"), f_header)
        sheet.write(header_row, 17, _("IND Backs"), f_header)
        sheet.write(header_row, 18, _("IND Workforce"), f_header)
        sheet.write(header_row, 19, _("IND Crumbs"), f_header)
        sheet.write(header_row, 20, _("IND Quality"), f_header)
        sheet.write(header_row, 21, _("IND Cleaning"), f_header)

        # TODO alternate dict list with almost grouped data (still problems with product and date)
        """
        grouped_rpt_tracing = self.env['mdc.rpt_tracing'].read_group(
            domain=[('id', 'in', rpt_tracing.ids)],
            fields=['lot_name', 'employee_code', 'product_id', 'shift_code',
                    'std_yield_product', 'std_yield_sp1', 'std_speed', 'gross_weight', 'product_weight',
                    'sp1_weight', 'quality', 'total_hours'],
            groupby=['lot_name', 'employee_code', 'shift_code'],
            lazy=False)
        for trace in grouped_rpt_tracing:
            pass
        """

        # write data rows
        row=header_row
        wlot_name = ''
        wemployee_code = ''
        wworkstation_name = ''
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wquality = 0
        wtotal_hours = 0
        wnumreg = 0
        wstart_date = False
        wend_date = False
        for obj in rpt_manufacturing:

            #min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date

            if (wlot_name != obj.lot_name) or (wemployee_code != obj.employee_code) or (wworkstation_name != obj.workstation_name):
                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.workstation_name)
                sheet.write(row, 1, obj.employee_code)
                sheet.write(row, 2, obj.employee_name)
                sheet.write(row, 3, obj.contract_name)
                sheet.write(row, 4, obj.lot_name)

                # std columns
                sheet.write(row, 11, obj.std_yield_product)
                sheet.write(row, 14, obj.std_yield_sp1)
                # sheet.write(row, 15, obj.std_speed)
                sheet.write(row, 16, obj.std_speed)
                # formulation columns
                sheet.write_formula(row, 10, '=G' + str(row+1) + '/F' + str(row+1), f_percent)
                sheet.write_formula(row, 12, '=H' + str(row+1) + '/F' + str(row+1), f_percent)
                sheet.write_formula(row, 13, '=(G' + str(row + 1) + '+H' + str(row + 1) + ')/F' + str(row + 1), f_percent)
                # Ind columns
                sheet.write_formula(row, 17, '=IF(L' + str(row + 1) + '= 0, 0, (K' + str(row + 1) + '/L' + str(row + 1) + ') * 100)', f_data)
                sheet.write_formula(row, 18, '=IF(Q' + str(row + 1) + '= 0, 0, (P' + str(row + 1) + '/Q' + str(row + 1) + ') * 100)', f_data)
                sheet.write_formula(row, 19, '=IF(O' + str(row + 1) + '= 0, 0, (M' + str(row + 1) + '/O' + str(row + 1) + ') * 100)', f_data)
                sheet.write(row, 20, obj.std_yield_sp1)
                sheet.write(row, 21, obj.std_speed)

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
            wworkstation_name = obj.workstation_name

            # Final Footer Row
            sheet.write_formula(row + 1, 5, '=SUM(F' + str(header_row + 1) + ':F' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 6, '=SUM(G' + str(header_row + 1) + ':G' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 7, '=SUM(H' + str(header_row + 1) + ':H' + str(row + 1) + ')', f_footer)

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
