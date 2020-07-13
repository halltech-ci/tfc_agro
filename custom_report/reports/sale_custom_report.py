# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

from datetime import datetime

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
        
    @api.one
    #@api.depends("lot_id")
    def _compute_lot_name(self):
        if self.lot_id:
            self.lot = self.lot_id.name
        else:
            self.lot = " "
    
    @api.one
    #@api.depends("lot_id")
    def _compute_payment_term(self):
        if self.order_id.payment_term_id:
            self.payment_term = self.order_id.payment_term_id.name
        else:
            self.payment_term = " "
    
    lot = fields.Char(string="Vessel", compute="_compute_lot_name")
    payment_term = fields.Char(string="Payment Term", compute="_compute_payment_term")
    date_order = fields.Datetime(string="Date Order", related="order_id.date_order", store=True)
    
    
    def Print_to_pdf(self):
        pass
    
    
            