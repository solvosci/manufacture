# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request

from . import websocket


# class SlvMdc(http.Controller):
#     @http.route('/mdc/mdc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mdc/mdc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mdc.listing', {
#             'root': '/mdc/mdc',
#             'objects': http.request.env['mdc.mdc'].search([]),
#         })

#     @http.route('/mdc/mdc/objects/<model("mdc.mdc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mdc.object', {
#             'object': obj
#         })


class CheckPoint(http.Controller):

    def _get_cp_user(self, request):
        return request.env.ref('mdc.mdc_user_cp')

    # Example route
    # TODO remove
    @http.route('/mdc/scales', type='http', auth='none')
    def scales(self):
        res = '''
            <html>
                <head>
                    <script language="JavaScript" src="/mdc/static/src/js/jquery-3.3.1.min.js"></script>
                </head>
                <body>
                    Scale list:
                    <table><tr><td>%s</td></tr></table>
                </body>
            </html>
        '''

        scales = request.env['mdc.scale'].sudo().search([])
        return res % '</td></tr><tr><td>'.join(scales.mapped('name'))

    @http.route('/mdc/cp/list', type='http', auth='none')
    def cp_list(self):
        chkpoints = request.env['mdc.chkpoint'].sudo(self._get_cp_user(request)).search([], order='order')
        return request.render(
            'mdc.chkpoint_list',
            {'chkpoints': chkpoints}
        )

    @http.route("/mdc/cp/win/<int:chkpoint_id>", type='http', auth='none')
    def cp_win(self, chkpoint_id):
        ws_session_data = websocket.get_session_data(request.env)
        chkpoints = request.env['mdc.chkpoint'].sudo(self._get_cp_user(request)).browse(chkpoint_id)
        return request.render(
            'mdc.chkpoint_win',
            {'chkpoints': chkpoints, 'ws_session_data': ws_session_data}
        )

    @http.route("/mdc/cp/win/<int:chkpoint_id>/lotactive", type='json', auth='none')
    def cp_win_lotactive(self, chkpoint_id):
        chkpoints = request.env['mdc.chkpoint'].sudo(self._get_cp_user(request)).browse(chkpoint_id)
        data = {
            'ckhpoint_id': chkpoint_id
        }
        try:
            if chkpoints:
                data['lotactive'] = ''
                if chkpoints[0].current_lot_active_id:
                    data['lotactive'] = chkpoints[0].current_lot_active_id.name
            else:
                raise UserError(_('Checkpoint #%s not found') % chkpoint_id)
        except UserError as e:
            data['err'] = e
        finally:
            return data

    @http.route("/mdc/cp/win/<int:chkpoint_id>/save", type='json', auth='none')
    def cp_win_save(self, chkpoint_id):
        data_in = dict(request.jsonrequest)
        data_in['chkpoint_id'] = chkpoint_id
        data_out = {
            'ckhpoint_id': chkpoint_id
        }

        DataWIn = request.env['mdc.data_win'].sudo(self._get_cp_user(request))
        try:
            datawin = DataWIn.from_cp_create(data_in)
            data_out['card_code'] = data_in['card_code']
            data_out['data_win_id'] = datawin.id
            data_out['lotactive'] = datawin.lot_id.name
            data_out['weight'] = '{0:.2f}'.format(datawin.weight)
            data_out['w_uom'] = datawin.w_uom_id.name
        except Exception as e:
            data_out['err'] = e
        finally:
            return data_out

    @http.route("/mdc/cp/wout/<int:chkpoint_id>", type='http', auth='none')
    def cp_win(self, chkpoint_id):
        ws_session_data = websocket.get_session_data(request.env)
        chkpoints = request.env['mdc.chkpoint'].sudo(self._get_cp_user(request)).browse(chkpoint_id)
        qualities = request.env['mdc.quality'].sudo(self._get_cp_user(request)).search([])
        return request.render(
            'mdc.chkpoint_wout',
            {'chkpoints': chkpoints, 'qualities': qualities, 'ws_session_data': ws_session_data}
        )

    @http.route('/mdc/cp/cardreg', type='http', auth='none')
    def cp_cardreg(self):
        devices = request.env['mdc.rfid_reader'].sudo(self._get_cp_user(request)).search([])
        card_categs = request.env['mdc.card_categ'].sudo(self._get_cp_user(request)).search([])
        employees = request.env['hr.employee'].sudo(self._get_cp_user(request)).search([('employee_code', '!=', '')])
        workstations = request.env['mdc.workstation'].sudo(self._get_cp_user(request)).search([])
        ws_session_data = websocket.get_session_data(request.env)
        return request.render(
            'mdc.chkpoint_card_registration',
            {'devices': devices, 'card_categs': card_categs, 'employees': employees, 'workstations': workstations,
             'ws_session_data': ws_session_data}
        )

    @http.route('/mdc/cp/cardreg/save', type='json', auth='none')
    def cp_cardreg_save(self):
        Card = request.env['mdc.card'].sudo(self._get_cp_user(request))
        try:
            card = Card.create({
                'name': request.jsonrequest['card_code'],
                'card_categ_id': request.jsonrequest['card_categ_id'],
                'employee_id': request.jsonrequest['employee_id'],
                'workstation_id': request.jsonrequest['workstation_id'],
            })
            return {
                'card_id': card.id
            }
        except Exception as e:
            return {
                'err': e
            }


