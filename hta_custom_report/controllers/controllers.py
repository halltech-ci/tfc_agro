# -*- coding: utf-8 -*-
from odoo import http

# class HtaCustomReport(http.Controller):
#     @http.route('/hta_custom_report/hta_custom_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hta_custom_report/hta_custom_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hta_custom_report.listing', {
#             'root': '/hta_custom_report/hta_custom_report',
#             'objects': http.request.env['hta_custom_report.hta_custom_report'].search([]),
#         })

#     @http.route('/hta_custom_report/hta_custom_report/objects/<model("hta_custom_report.hta_custom_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hta_custom_report.object', {
#             'object': obj
#         })