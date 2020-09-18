# -*- coding: utf-8 -*-
from odoo import http

# class HtaPartnerLedger(http.Controller):
#     @http.route('/hta_partner_ledger/hta_partner_ledger/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hta_partner_ledger/hta_partner_ledger/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hta_partner_ledger.listing', {
#             'root': '/hta_partner_ledger/hta_partner_ledger',
#             'objects': http.request.env['hta_partner_ledger.hta_partner_ledger'].search([]),
#         })

#     @http.route('/hta_partner_ledger/hta_partner_ledger/objects/<model("hta_partner_ledger.hta_partner_ledger"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hta_partner_ledger.object', {
#             'object': obj
#         })