# -*- coding: utf-8 -*-
from odoo import http
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

    @http.route('/mdc/cp/in', type='http', auth='none')
    def cp_in(self):
        session_id = websocket.ws_create()

        res = '''
            <html>
                <head>
                    <title>IN - MDC CP</title>
                    <script language="JavaScript" src="/mdc/static/src/js/jquery-3.3.1.min.js"></script>
                    <script language="JavaScript" src="/mdc/static/src/js/cp_in.js"></script>
                </head>
                <body>
                    <div>MCD CP: <a href="/web">Home</a></div>
                    <hr>
                    Session_id: <input type="text" id="session_id" value="%s"/>
                </body>
            </html>        
        '''

        return res % session_id