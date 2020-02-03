# -*- coding: utf-8 -*-
from odoo import http

# class TfcCustom(http.Controller):
#     @http.route('/tfc_custom/tfc_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tfc_custom/tfc_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tfc_custom.listing', {
#             'root': '/tfc_custom/tfc_custom',
#             'objects': http.request.env['tfc_custom.tfc_custom'].search([]),
#         })

#     @http.route('/tfc_custom/tfc_custom/objects/<model("tfc_custom.tfc_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tfc_custom.object', {
#             'object': obj
#         })