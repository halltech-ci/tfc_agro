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
            self.lot = self.lot_id
        else:
            self.lot = " "
    
    lot = fields.Char(string="Lot_id", compute="_compute_lot_name")
    
    
            