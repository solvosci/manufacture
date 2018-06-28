from odoo import models

class Report1Xlsx(models.AbstractModel):
    _name = 'report.mdc.cumulative_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, data_win):
        report_name = "cumulative_report"
        sheet = workbook.add_worksheet("cumulative report")
        fila=0
        for obj in data_win:
            sheet.write(fila, 0, obj.line_id)
            sheet.write(fila, 1, obj.lot_id)
            fila=fila+1