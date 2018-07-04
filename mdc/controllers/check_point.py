# -*- coding: utf-8 -*-
from odoo import http, _
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
        lotactives = request.env['mdc.lot_active'].sudo(self._get_cp_user(request)).search(
            [('chkpoint_id', '=', chkpoint_id)])
        if lotactives:
            return {
                'ckhpoint_id': chkpoint_id,
                'lotactive': lotactives[0].lot_id.name
            }
        else:
            return {
                'ckhpoint_id': chkpoint_id,
                'err': _('There are no active lots for this checkpoint')
            }

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


