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
    dic_formats["header_ind"] = {'bold': True,
                             'font_color': '#004080',
                             'bg_color': '#BBDDBB',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
                             'align': 'center',
                             'size': 12}
    dic_formats["header_ind_old"] = {'bold': True,
                             'font_color': '#004080',
                             'bg_color': '#DDDDDD',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
                             'align': 'center',
                             'size': 12}
    dic_formats["footer"] = {'bold': True,
                             'font_color': '#003060',
                             'bg_color': '#CCCCCC',
                             'bottom': True,
                             'top': True,
                             'text_wrap': True,
                             'align': 'center',
                             'size': 12}
    dic_formats["data"] = {'align': 'center'}
    dic_formats["percent"] = {'align': 'center',
                            'num_format': '0.00%'}
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
        f_header_ind = workbook.add_format(f_cells["header_ind"])
        f_filter = workbook.add_format(f_cells["filter"])
        f_percent = workbook.add_format(f_cells ["percent"])
        f_data = workbook.add_format(f_cells ["data"])

        # Set columns widths
        sheet.set_column('A:W', 13)
        sheet.set_column('C:D', 40) # Employee name and STD name columns
        sheet.set_column('E:E', 16) # Client name

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

        header_row = 5
        header_row_str = str(header_row + 1)
        # write column header ------------------------------------------
        sheet.write('A' + header_row_str, _("MO"), f_header)
        sheet.write('B' + header_row_str, _("Employee Code"), f_header)
        sheet.write('C' + header_row_str, _("Employee Name"), f_header)
        sheet.write('D' + header_row_str, _("STD"), f_header)
        sheet.write('E' + header_row_str, _("Client"), f_header)
        sheet.write('F' + header_row_str, _("Shift"), f_header)
        sheet.write('G' + header_row_str, _("Gross"), f_header)
        sheet.write('H' + header_row_str, _("Backs"), f_header)
        sheet.write('I' + header_row_str, _("Crumbs"), f_header)
        sheet.write('J' + header_row_str, _("Quality"), f_header)
        sheet.write('K' + header_row_str, _("Time"), f_header)
        sheet.write('L' + header_row_str, _("% Backs"), f_header)
        sheet.write('M' + header_row_str, _("STD Back"), f_header)
        sheet.write('N' + header_row_str, _("% Crumbs"), f_header)
        sheet.write('O' + header_row_str, _("% Total Yield"), f_header)
        sheet.write('P' + header_row_str, _("STD Crumbs"), f_header)
        sheet.write('Q' + header_row_str, _("MO."), f_header)
        sheet.write('R' + header_row_str, _("STD MO"), f_header)
        sheet.write('S' + header_row_str, _("IND Backs"), f_header_ind)
        sheet.write('T' + header_row_str, _("IND MO"), f_header_ind)
        sheet.write('U' + header_row_str, _("IND Crumbs"), f_header_ind)
        sheet.write('V' + header_row_str, _("IND Quality"), f_header_ind)
        sheet.write('W' + header_row_str, _("IND Cleaning"), f_header_ind)
        # -------------------------------------------------------

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
        # Filters ---------
        wstart_date = False
        wend_date = False
        wlot_filter= ''
        wshift_filter = ''
        wlot_filter_uniq = True
        wshift_filter_uniq = True
        # -----------------

        for obj in rpt_tracing:

            #Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date
            # lot
            if wlot_filter == '':
                wlot_filter = obj.lot_name
            # shift
            if wshift_filter == '':
                    wshift_filter = obj.shift_code
            # ------------------------------------------------

            if (wlot_name != obj.lot_name) or (wemployee_code != obj.employee_code) or (wshift_code != obj.shift_code):
                # lot Filter
                if wlot_filter != obj.lot_name:
                    wlot_filter_uniq = False
                # shift Filter
                if wshift_filter != obj.shift_code:
                    wshift_filter_uniq = False

                row = row + 1

                # direct data from view database
                product_name = obj.product_id.name_get()[0][1]
                sheet.write(row, 0, obj.lot_name, f_data)
                sheet.write(row, 1, obj.employee_code, f_data)
                sheet.write(row, 2, obj.employee_name, f_data)
                sheet.write(row, 3, product_name, f_data)
                sheet.write(row, 4, obj.client_name, f_data)
                sheet.write(row, 5, obj.shift_code, f_data)
                # std columns
                sheet.write(row, 12, obj.std_yield_product, f_data)
                sheet.write(row, 15, obj.std_yield_sp1, f_data)
                sheet.write(row, 17, obj.std_speed, f_data)
                # formulation columns
                sheet.write_formula(row, 11, '=IF(G' + str(row + 1) + '= 0, 0, H' + str(row+1) + '/G' + str(row+1) + ')', f_percent) # - % Backs
                sheet.write_formula(row, 13, '=IF(G' + str(row + 1) + '= 0, 0, I' + str(row+1) + '/G' + str(row+1) + ')', f_percent) # - % Crumbs
                sheet.write_formula(row, 14, '=IF(G' + str(row + 1) + '= 0, 0, (H' + str(row + 1) + '+I' + str(row + 1) + ')/G' + str(row + 1) + ')', f_percent) # - % Total Yield
                sheet.write_formula(row, 15, '=IF(G' + str(row + 1) + '= 0, 0, (K' + str(row + 1) + ' * 60)/G' + str(row + 1) + ')', f_data) # - MO
                # Ind columns
                sheet.write_formula(row, 18, '=IF(M' + str(row + 1) + '= 0, 0, (L' + str(row + 1) + '/M' + str(row + 1) + '/1,15) * 100)', f_data) # - IND Backs
                sheet.write_formula(row, 19, '=IF(R' + str(row + 1) + '= 0, 0, (Q' + str(row + 1) + '/R' + str(row + 1) + '/1,15) * 100)', f_data) # - IND MO
                sheet.write_formula(row, 20, '=IF(N' + str(row + 1) + '= 0, 0, (P' + str(row + 1) + '/N' + str(row + 1) + '/1,15) * 100)', f_data) # - IND Crumbs
                sheet.write_formula(row, 21, '=J' + str(row + 1), f_data) # - IND Quality
                sheet.write_formula(row, 22, '0,6 * S' + str(row + 1) + ' + 0,3 * T' + str(row + 1) + ' + 0,1 * V' + str(row + 1), f_data) # - IND Cleaning

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
            wquality += obj.quality * obj.product_weight
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if wproduct_weight == 0:
                wquality=0
            else:
                wquality = wquality / wproduct_weight

            #columns with grouped data
            sheet.write(row, 6, wgross_weight, f_data)
            sheet.write(row, 7, wproduct_weight, f_data)
            sheet.write(row, 8, wsp1_weight, f_data)
            sheet.write(row, 9, wquality, f_data)
            sheet.write(row, 10, wtotal_hours, f_data)

            wlot_name = obj.lot_name
            wemployee_code = obj.employee_code
            wshift_code = obj.shift_code

        # Write Filter -----------------------------------------------
        datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
        if wstart_date == wend_date:
            datefilter = _("Date: %s") % wstart_date
        if wlot_filter_uniq:
            datefilter = datefilter + ' // ' + _("Lot: %s") % wlot_filter
        if wshift_filter_uniq:
            datefilter = datefilter + ' // ' + _("Shift: %s") % wshift_filter
        sheet.write(2, 2, datefilter, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
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
        f_header_ind = workbook.add_format(f_cells["header_ind"])
        f_header_ind_old = workbook.add_format(f_cells["header_ind_old"])
        f_filter = workbook.add_format(f_cells["filter"])
        f_percent = workbook.add_format(f_cells ["percent"])
        f_data = workbook.add_format(f_cells ["data"])
        f_footer = workbook.add_format(f_cells["footer"])

        # Set columns widths
        sheet.set_column('A:AD', 13)
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
        header_row_str = str(header_row+1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str , _("Workstation"), f_header)
        sheet.write('B' + header_row_str, _("Employee Code"), f_header)
        sheet.write('C' + header_row_str, _("Employee Name"), f_header)
        sheet.write('D' + header_row_str, _("Contract"), f_header)
        sheet.write('E' + header_row_str, _("MO"), f_header)
        sheet.write('F' + header_row_str, _("Gross"), f_header)
        sheet.write('G' + header_row_str, _("Backs"), f_header)
        sheet.write('H' + header_row_str, _("Crumbs"), f_header)
        sheet.write('I' + header_row_str, _("Shift Change Gross"), f_header)
        sheet.write('J' + header_row_str, _("Shift Change Backs"), f_header)
        sheet.write('K' + header_row_str, _("Shift Change Crumbs"), f_header)
        sheet.write('L' + header_row_str, _("Quality"), f_header)
        sheet.write('M' + header_row_str, _("Time"), f_header)
        sheet.write('N' + header_row_str, _("% Backs"), f_header)
        sheet.write('O' + header_row_str, _("STD Back"), f_header)
        sheet.write('P' + header_row_str, _("% Crumbs"), f_header)
        sheet.write('Q' + header_row_str, _("% Total Yield"), f_header)
        sheet.write('R' + header_row_str, _("STD Crumbs"), f_header)
        sheet.write('S' + header_row_str, _("MO."), f_header)
        sheet.write('T' + header_row_str, _("STD MO"), f_header)
        sheet.write('U' + header_row_str, _("IND Backs"), f_header_ind)
        sheet.write('V' + header_row_str, _("IND MO"), f_header_ind)
        sheet.write('W' + header_row_str, _("IND Crumbs"), f_header_ind)
        sheet.write('X' + header_row_str, _("IND Quality"), f_header_ind)
        sheet.write('Y' + header_row_str, _("IND Cleaning"), f_header_ind)
        sheet.write('Z' + header_row_str, _("Box Backs"), f_header)
        sheet.write('AA' + header_row_str, _("Box Crumbs"), f_header)
        sheet.write('AB' + header_row_str, _("MO"), f_header_ind_old)
        sheet.write('AC' + header_row_str, _("IND MO"), f_header_ind_old)
        sheet.write('AD' + header_row_str, _("IND Cleaning"), f_header_ind_old)
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row=header_row
        wlot_name = ''
        wemployee_code = ''
        wworkstation_name = ''
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wshared_gross_weight = 0
        wshared_product_weight = 0
        wshared_sp1_weight = 0
        wproduct_boxes =0
        wsp1_boxes =0
        wquality = 0
        wtotal_hours = 0
        wnumreg = 0
        # Filters ---------
        wstart_date = False
        wend_date = False
        wlot_filter = ''
        wshift_filter = ''
        wlot_filter_uniq = True
        wshift_filter_uniq = True
        # -----------------

        for obj in rpt_manufacturing:

            # Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date
            # lot
            if wlot_filter == '':
                wlot_filter = obj.lot_name
            # shift
            if wshift_filter == '':
                wshift_filter = obj.shift_code
            # ------------------------------------------------

            # shift Filter
            if wshift_filter != obj.shift_code:
                wshift_filter_uniq = False

            if (wlot_name != obj.lot_name) or (wemployee_code != obj.employee_code) or (wworkstation_name != obj.workstation_name):
                # lot Filter
                if wlot_filter != obj.lot_name:
                    wlot_filter_uniq = False

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.workstation_name, f_data)
                sheet.write(row, 1, obj.employee_code, f_data)
                sheet.write(row, 2, obj.employee_name, f_data)
                sheet.write(row, 3, obj.contract_name, f_data)
                sheet.write(row, 4, obj.lot_name, f_data)
                # std columns
                sheet.write(row, 14, obj.std_yield_product, f_data)
                sheet.write(row, 17, obj.std_yield_sp1, f_data)
                sheet.write(row, 19, obj.std_speed, f_data)
                # formulation columns
                sheet.write_formula(row, 13, '=IF(F' + str(row + 1) + '= 0, 0, G' + str(row + 1) + '/F' + str(row + 1) + ')', f_percent)  # - % Backs
                sheet.write_formula(row, 15, '=IF(F' + str(row + 1) + '= 0, 0, H' + str(row + 1) + '/F' + str(row + 1) + ')', f_percent)  # - % Crumbs
                sheet.write_formula(row, 16, '=IF(F' + str(row + 1) + '= 0, 0, (G' + str(row + 1) + '+H' + str(row + 1) + ')/F' + str(row + 1) + ')' ,f_percent)  # - % Total Yield
                sheet.write_formula(row, 18, '=IF(F' + str(row + 1) + '= 0, 0, (M' + str(row + 1) + ' * 60)/F' + str(row + 1) + ')', f_data)  # - MO
                # Ind columns
                sheet.write_formula(row, 20, '=IF(O' + str(row + 1) + '= 0, 0, (N' + str(row + 1) + '/O' + str(row + 1) + '/1,15) * 100)', f_data) # - IND Backs
                sheet.write_formula(row, 21, '=IF(T' + str(row + 1) + '= 0, 0, (S' + str(row + 1) + '/T' + str(row + 1) + '/1,15) * 100)', f_data) # - IND MO
                sheet.write_formula(row, 22, '=IF(P' + str(row + 1) + '= 0, 0, (R' + str(row + 1) + '/P' + str(row + 1) + '/1,15) * 100)', f_data) # - IND Crumbs
                sheet.write_formula(row, 23, '=L' + str(row + 1), f_data) # - IND Quality
                sheet.write_formula(row, 24, '0,6 * U' + str(row + 1) + ' + 0,3 * V' + str(row + 1) + ' + 0,1 * X' + str(row + 1), f_data) # - IND Cleaning
                # Ind Old Columns
                sheet.write_formula(row, 27, 'S' + str(row + 1) + '*' + str(obj.coef_weight_lot), f_data)  # - MO
                sheet.write_formula(row, 28, '=IF(T' + str(row + 1) + '= 0, 0, (AB' + str(row + 1) + '/T' + str(row + 1) + '/1,15) * 100)', f_data)  # - IND MO
                sheet.write_formula(row, 29, '0,6 * U' + str(row + 1) + ' + 0,3 * AC' + str(row + 1) + ' + 0,1 * X' + str(row + 1), f_data)  # - IND Cleaning

                wgross_weight = 0
                wproduct_weight = 0
                wsp1_weight = 0
                wshared_gross_weight = 0
                wshared_product_weight = 0
                wshared_sp1_weight = 0
                wproduct_boxes = 0
                wsp1_boxes = 0
                wquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight += obj.gross_weight
            wproduct_weight += obj.product_weight
            wsp1_weight += obj.sp1_weight
            wshared_gross_weight += obj.shared_gross_weight
            wshared_product_weight += obj.shared_product_weight
            wshared_sp1_weight += obj.shared_sp1_weight
            wproduct_boxes += obj.product_boxes
            wsp1_boxes += obj.sp1_boxes
            wquality += obj.quality * obj.product_weight
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if (wproduct_weight + wshared_product_weight/2) == 0:
                wquality=0
            else:
                wquality = wquality/(wproduct_weight + wshared_product_weight/2)

            #columns with grouped data
            sheet.write(row, 5, wgross_weight, f_data)
            sheet.write(row, 6, wproduct_weight, f_data)
            sheet.write(row, 7, wsp1_weight, f_data)
            sheet.write(row, 8, wshared_gross_weight, f_data)
            sheet.write(row, 9, wshared_product_weight, f_data)
            sheet.write(row, 10, wshared_sp1_weight, f_data)
            sheet.write(row, 11, wquality, f_data)
            sheet.write(row, 12, wtotal_hours, f_data)
            sheet.write(row, 25, wproduct_boxes, f_data)
            sheet.write(row, 26, wsp1_boxes, f_data)

            wlot_name = obj.lot_name
            wemployee_code = obj.employee_code
            wworkstation_name = obj.workstation_name

            # Final Footer Row ------------------------------------------
            for numcol in range (0, 30):
                sheet.write(row + 1, numcol, '' ,f_footer)
            sheet.write_formula(row + 1, 5, '=SUM(F' + str(header_row + 1) + ':F' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 6, '=SUM(G' + str(header_row + 1) + ':G' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 7, '=SUM(H' + str(header_row + 1) + ':H' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 8, '=SUM(I' + str(header_row + 1) + ':I' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 9, '=SUM(J' + str(header_row + 1) + ':J' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 10, '=SUM(K' + str(header_row + 1) + ':K' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 12, '=SUM(M' + str(header_row + 1) + ':M' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 25, '=SUM(Z' + str(header_row + 1) + ':Z' + str(row + 1) + ')', f_footer)
            sheet.write_formula(row + 1, 26, '=SUM(AA' + str(header_row + 1) + ':AA' + str(row + 1) + ')', f_footer)

            # Write Filter -----------------------------------------------
            datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
            if wstart_date == wend_date:
                datefilter = _("Date: %s") % wstart_date
            if wlot_filter_uniq:
                datefilter = datefilter + ' // ' + _("Lot: %s") % wlot_filter
            if wshift_filter_uniq:
                datefilter = datefilter + ' // ' + _("Shift: %s") % wshift_filter
            sheet.write(2, 2, datefilter, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)


class ReportRptIndicatorsXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_indicators'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, rpt_indicators):
        report_name = "rpt_indicators"
        sheet = workbook.add_worksheet("Indicators Report")

        # General sheet style
        sheet.set_landscape()
        sheet.repeat_rows(0,5)
        sheet.hide_gridlines(3)

        # get Formats Dictionary from standard function formats
        f_cells = formats()
        f_title = workbook.add_format(f_cells["title"])
        f_header = workbook.add_format(f_cells ["header"])
        f_header_ind = workbook.add_format(f_cells["header_ind"])
        f_filter = workbook.add_format(f_cells["filter"])
        f_percent = workbook.add_format(f_cells ["percent"])
        f_data = workbook.add_format(f_cells ["data"])
        f_footer = workbook.add_format(f_cells["footer"])

        # Set columns widths
        sheet.set_column('A:T', 13)
        sheet.set_column('E:O', 0, None, {'hidden': 1})
        sheet.set_column('B:B', 40) # Employee name

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
        sheet.write(1, 2, _("INDICATORS REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row = 5
        header_row_str = str(header_row + 1)
        # write column header ----------------------------------------
        # Hidden columns from D to O ---------------------------------
        sheet.write('A' + header_row_str, _("Employee Code"), f_header)
        sheet.write('B' + header_row_str, _("Employee Name"), f_header)
        sheet.write('C' + header_row_str, _("Shift"), f_header)
        sheet.write('D' + header_row_str, _("MO"), f_header)
        sheet.write('E' + header_row_str, _("Gross"), f_header)
        sheet.write('F' + header_row_str, _("Backs"), f_header)
        sheet.write('G' + header_row_str, _("Crumbs"), f_header)
        sheet.write('H' + header_row_str, _("Quality"), f_header)
        sheet.write('I' + header_row_str, _("Time"), f_header)
        sheet.write('J' + header_row_str, _("% Backs"), f_header)
        sheet.write('K' + header_row_str, _("STD Back"), f_header)
        sheet.write('L' + header_row_str, _("% Crumbs"), f_header)
        sheet.write('M' + header_row_str, _("STD Crumbs"), f_header)
        sheet.write('N' + header_row_str, _("MO."), f_header)
        sheet.write('O' + header_row_str, _("STD MO"), f_header)
        sheet.write('P' + header_row_str, _("IND Backs"), f_header_ind)
        sheet.write('Q' + header_row_str, _("IND MO"), f_header_ind)
        sheet.write('R' + header_row_str, _("IND Crumbs"), f_header_ind)
        sheet.write('S' + header_row_str, _("IND Quality"), f_header_ind)
        sheet.write('T' + header_row_str, _("IND Cleaning"), f_header_ind)
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row=header_row
        wlot_name = ''
        wemployee_code = ''
        wshift_code = ''
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wshared_gross_weight = 0
        wshared_product_weight = 0
        wshared_sp1_weight = 0
        wquality = 0
        wtotal_hours = 0
        wnumreg = 0
        # Filters ---------
        wstart_date = False
        wend_date = False
        wlot_filter = ''
        wshift_filter = ''
        wlot_filter_uniq = True
        wshift_filter_uniq = True
        # -----------------

        for obj in rpt_indicators:

            # Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date
            # lot
            if wlot_filter == '':
                wlot_filter = obj.lot_name
            # shift
            if wshift_filter == '':
                wshift_filter = obj.shift_code
            # ------------------------------------------------

            # lot Filter
            if wlot_filter != obj.lot_name:
                wlot_filter_uniq = False

            if (wemployee_code != obj.employee_code) or (wshift_code != obj.shift_code):
                # shift Filter
                if wshift_filter != obj.shift_code:
                    wshift_filter_uniq = False

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.employee_code, f_data)
                sheet.write(row, 1, obj.employee_name, f_data)
                sheet.write(row, 2, obj.shift_code, f_data)
                sheet.write(row, 3, obj.lot_name, f_data)
                # std columns
                sheet.write(row, 9, obj.std_yield_product, f_data)
                sheet.write(row, 11, obj.std_yield_sp1, f_data)
                sheet.write(row, 13, obj.std_speed, f_data)
                # formulation columns
                sheet.write_formula(row, 10, '=F' + str(row + 1) + '/E' + str(row + 1), f_percent)  # - % Backs
                sheet.write_formula(row, 12, '=G' + str(row + 1) + '/E' + str(row + 1), f_percent)  # - % Crumbs
                sheet.write_formula(row, 14, '=(I' + str(row + 1) + ' * 60)/E' + str(row + 1), f_data)  # - MO
                # Ind columns
                sheet.write_formula(row, 15, '=IF(K' + str(row + 1) + '= 0, 0, (J' + str(row + 1) + '/K' + str(row + 1) + '/1,15) * 100)', f_data)  # - IND Backs
                sheet.write_formula(row, 16, '=IF(N' + str(row + 1) + '= 0, 0, (O' + str(row + 1) + '/N' + str(row + 1) + '/1,15) * 100)', f_data)  # - IND MO
                sheet.write_formula(row, 17, '=IF(L' + str(row + 1) + '= 0, 0, (M' + str(row + 1) + '/L' + str(row + 1) + '/1,15) * 100)', f_data)  # - IND Crumbs
                sheet.write_formula(row, 18, '=H' + str(row + 1), f_data)  # - IND Quality
                sheet.write_formula(row, 19, '0,6 * P' + str(row + 1) + ' + 0,3 * Q' + str(row + 1) + ' + 0,1 * S' + str(row + 1), f_data)  # - IND Cleaning

                wgross_weight = 0
                wproduct_weight = 0
                wsp1_weight = 0
                wshared_gross_weight = 0
                wshared_product_weight = 0
                wshared_sp1_weight = 0
                wquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight += obj.gross_weight
            wproduct_weight += obj.product_weight
            wsp1_weight += obj.sp1_weight
            wshared_gross_weight += obj.shared_gross_weight
            wshared_product_weight += obj.shared_product_weight
            wshared_sp1_weight += obj.shared_sp1_weight
            wquality += obj.quality * obj.product_weight
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if (wproduct_weight + wshared_product_weight/2) == 0:
                wquality=0
            else:
                wquality = wquality/(wproduct_weight + wshared_product_weight/2)

            #columns with grouped data
            sheet.write(row, 4, wgross_weight, f_data)
            sheet.write(row, 5, wproduct_weight, f_data)
            sheet.write(row, 6, wsp1_weight, f_data)
            sheet.write(row, 7, wquality, f_data)
            sheet.write(row, 8, wtotal_hours, f_data)

            wlot_name = obj.lot_name
            wemployee_code = obj.employee_code
            wshift_code = obj.shift_code

            # Final Footer Row

            # Write Filter -----------------------------------------------
            datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
            if wstart_date == wend_date:
                datefilter = _("Date: %s") % wstart_date
            if wlot_filter_uniq:
                datefilter = datefilter + ' // ' + _("Lot: %s") % wlot_filter
            if wshift_filter_uniq:
                datefilter = datefilter + ' // ' + _("Shift: %s") % wshift_filter
            sheet.write(2, 2, datefilter, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)


class ReportRptCumulativeXlsx(models.AbstractModel):
    _name = 'report.mdc.rpt_cumulative'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, rpt_cumulative):
        report_name = "rpt_cumulative"
        sheet = workbook.add_worksheet("Cumulative Report")

        # General sheet style
        sheet.set_landscape()
        sheet.repeat_rows(0,5)
        sheet.hide_gridlines(3)

        # get Formats Dictionary from standard function formats
        f_cells = formats()
        f_title = workbook.add_format(f_cells["title"])
        f_header = workbook.add_format(f_cells ["header"])
        f_header_ind = workbook.add_format(f_cells["header_ind"])
        f_filter = workbook.add_format(f_cells["filter"])
        f_percent = workbook.add_format(f_cells ["percent"])
        f_data = workbook.add_format(f_cells ["data"])
        f_footer = workbook.add_format(f_cells["footer"])

        # Set columns widths
        sheet.set_column('A:X', 13)
        sheet.set_column('O:S', 0, None, {'hidden': 1})
        sheet.set_column('B:B', 40) # Employee name

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
        sheet.write(1, 2, _("CUMULATIVE REPORT"), f_title)

        # write Filter
        sheet.write(2, 2, _("Date From:"), f_filter)

        header_row = 5
        header_row_str = str(header_row + 1)
        # write column header ----------------------------------------
        sheet.write('A' + header_row_str, _("Employee Code"), f_header)
        sheet.write('B' + header_row_str, _("Employee Name"), f_header)
        sheet.write('C' + header_row_str, _("Gross"), f_header)
        sheet.write('D' + header_row_str, _("Backs"), f_header)
        sheet.write('E' + header_row_str, _("Crumbs"), f_header)
        sheet.write('F' + header_row_str, _("Shift Change Gross"), f_header)
        sheet.write('G' + header_row_str, _("Shift Change Backs"), f_header)
        sheet.write('H' + header_row_str, _("Shift Change Crumbs"), f_header)
        sheet.write('I' + header_row_str, _("Quality"), f_header)
        sheet.write('J' + header_row_str, _("% Backs"), f_header)
        sheet.write('K' + header_row_str, _("% Crumbs"), f_header)
        sheet.write('L' + header_row_str, _("% Total Yield"), f_header)
        sheet.write('M' + header_row_str, _("Waste"), f_header)
        sheet.write('N' + header_row_str, _("% Waste"), f_header)
        sheet.write('O' + header_row_str, _("Time"), f_header)
        sheet.write('P' + header_row_str, _("MO."), f_header)
        sheet.write('Q' + header_row_str, _("STD Back"), f_header)
        sheet.write('R' + header_row_str, _("STD Crumbs"), f_header)
        sheet.write('S' + header_row_str, _("STD MO"), f_header)
        sheet.write('T' + header_row_str, _("IND Backs"), f_header_ind)
        sheet.write('U' + header_row_str, _("IND MO"), f_header_ind)
        sheet.write('V' + header_row_str, _("IND Crumbs"), f_header_ind)
        sheet.write('W' + header_row_str, _("IND Quality"), f_header_ind)
        sheet.write('X' + header_row_str, _("IND Cleaning"), f_header_ind)
        # -------------------------------------------------------

        # TODO alternate dict list with almost grouped data (still problems with product and date)

        # write data rows
        row=header_row
        wlot_name = ''
        wemployee_code = ''
        wgross_weight = 0
        wproduct_weight = 0
        wsp1_weight = 0
        wshared_gross_weight = 0
        wshared_product_weight = 0
        wshared_sp1_weight = 0
        wquality = 0
        wtotal_hours = 0
        wnumreg = 0
        # Filters ---------
        wstart_date = False
        wend_date = False
        wlot_filter = ''
        wlot_filter_uniq = True
        # -----------------

        for obj in rpt_cumulative:

            # Filters: ----------------------------------------
            # min a max date
            if wstart_date is False or wstart_date > obj.create_date:
                wstart_date = obj.create_date
            if wend_date is False or wend_date < obj.create_date:
                wend_date = obj.create_date
            # lot
            if wlot_filter == '':
                wlot_filter = obj.lot_name
            # ------------------------------------------------

            # lot Filter
            if wlot_filter != obj.lot_name:
                wlot_filter_uniq = False

            if (wemployee_code != obj.employee_code):

                row = row + 1

                # direct data from view database
                sheet.write(row, 0, obj.employee_code, f_data)
                sheet.write(row, 1, obj.employee_name, f_data)

                # std columns
                sheet.write(row, 16, obj.std_yield_product, f_data)
                sheet.write(row, 17, obj.std_yield_sp1, f_data)
                sheet.write(row, 18, obj.std_speed, f_data)
                # formulation columns
                sheet.write_formula(row, 9, '=IF(C' + str(row + 1) + '= 0, 0, D' + str(row + 1) + '/C' + str(row + 1) + ')', f_percent)  # - % Backs
                sheet.write_formula(row, 10, '=IF(C' + str(row + 1) + '= 0, 0, E' + str(row + 1) + '/C' + str(row + 1) + ')', f_percent)  # - % Crumbs
                sheet.write_formula(row, 11, '=IF(C' + str(row + 1) + '= 0, 0, (D' + str(row + 1) + '+E' + str(row + 1) + ')/C' + str(row + 1) + ')', f_percent) # - % Total Yield
                sheet.write_formula(row, 12, '=(C' + str(row + 1) + '-D' + str(row + 1) + '-E' + str(row + 1),  f_data)  # - Waste
                sheet.write_formula(row, 13, '=IF(C' + str(row + 1) + '= 0, 0, (M' + str(row + 1) + ')/C' + str(row + 1) + ')', f_percent)  # - % Waste
                sheet.write_formula(row, 15, '=IF(C' + str(row + 1) + '= 0, 0, (I' + str(row + 1) + ' * 60)/C' + str(row + 1) + ')', f_data)  # - MO
                # Ind columns
                sheet.write_formula(row, 19, '=IF(Q' + str(row + 1) + '= 0, 0, (J' + str(row + 1) + '/Q' + str(row + 1) + '/1,15) * 100)', f_data)  # - IND Backs
                sheet.write_formula(row, 20, '=IF(S' + str(row + 1) + '= 0, 0, (P' + str(row + 1) + '/S' + str(row + 1) + '/1,15) * 100)', f_data)  # - IND MO
                sheet.write_formula(row, 21, '=IF(K' + str(row + 1) + '= 0, 0, (R' + str(row + 1) + '/K' + str(row + 1) + '/1,15) * 100)', f_data)  # - IND Crumbs
                sheet.write_formula(row, 22, '=I' + str(row + 1), f_data)  # - IND Quality
                sheet.write_formula(row, 23, '0,6 * T' + str(row + 1) + ' + 0,3 * V' + str(row + 1) + ' + 0,1 * W' + str(row + 1), f_data)  # - IND Cleaning

                wgross_weight = 0
                wproduct_weight = 0
                wsp1_weight = 0
                wshared_gross_weight = 0
                wshared_product_weight = 0
                wshared_sp1_weight = 0
                wquality = 0
                wtotal_hours = 0
                wnumreg = 0

            # grouped data vars
            wgross_weight += obj.gross_weight
            wproduct_weight += obj.product_weight
            wsp1_weight += obj.sp1_weight
            wshared_gross_weight += obj.shared_gross_weight
            wshared_product_weight += obj.shared_product_weight
            wshared_sp1_weight += obj.shared_sp1_weight
            wquality += obj.quality * obj.product_weight
            wtotal_hours += obj.total_hours
            wnumreg += 1

            if (wproduct_weight + wshared_product_weight/2) == 0:
                wquality=0
            else:
                wquality = wquality/(wproduct_weight + wshared_product_weight/2)

            #columns with grouped data
            sheet.write(row, 2, wgross_weight, f_data)
            sheet.write(row, 3, wproduct_weight, f_data)
            sheet.write(row, 4, wsp1_weight, f_data)
            sheet.write(row, 5, wshared_gross_weight, f_data)
            sheet.write(row, 6, wshared_product_weight, f_data)
            sheet.write(row, 7, wshared_sp1_weight, f_data)
            sheet.write(row, 8, wquality, f_data)
            sheet.write(row, 14, wtotal_hours, f_data)

            wlot_name = obj.lot_name
            wemployee_code = obj.employee_code


            # Final Footer Row

        # write Filter
        datefilter = _("Date From: %s to %s") % (wstart_date, wend_date)
        if wstart_date == wend_date:
            datefilter = _("Date: #%s") % wstart_date
        sheet.write(2, 2, datefilter, f_filter)

        # Final Presentation
        # Select the cells back to image & zoom presentation & split & freeze_panes
        sheet.set_selection('A6')
        sheet.set_zoom(80)
        # sheet.split_panes(60,0,5,0)