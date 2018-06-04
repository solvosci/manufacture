# -*- coding: utf-8 -*-
from odoo import http

# class SlvMdc(http.Controller):
#     @http.route('/slv_mdc/slv_mdc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/slv_mdc/slv_mdc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('slv_mdc.listing', {
#             'root': '/slv_mdc/slv_mdc',
#             'objects': http.request.env['slv_mdc.slv_mdc'].search([]),
#         })

#     @http.route('/slv_mdc/slv_mdc/objects/<model("slv_mdc.slv_mdc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('slv_mdc.object', {
#             'object': obj
#         })