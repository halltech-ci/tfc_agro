# -*- coding: utf-8 -*-
from odoo import http

# class HtaSaleReports(http.Controller):
#     @http.route('/hta_sale_reports/hta_sale_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hta_sale_reports/hta_sale_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hta_sale_reports.listing', {
#             'root': '/hta_sale_reports/hta_sale_reports',
#             'objects': http.request.env['hta_sale_reports.hta_sale_reports'].search([]),
#         })

#     @http.route('/hta_sale_reports/hta_sale_reports/objects/<model("hta_sale_reports.hta_sale_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hta_sale_reports.object', {
#             'object': obj
#         })