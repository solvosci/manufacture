# -*- coding: utf-8 -*-
from odoo import http

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