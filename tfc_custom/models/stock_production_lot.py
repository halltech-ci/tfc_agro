# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class tfc_custom(models.Model):
#     _name = 'tfc_custom.tfc_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    
    product_sale_qty = fields.Float('Saled Qty', compute='_sale_qty')
    product_purchase_qty = fields.Float('Purchased Qty', compute='_purchase_qty')
    
    @api.one
    def _sale_qty(self):
        # We only care for the quants in internal or transit locations.
        quants = self.quant_ids.filtered(lambda q: q.location_id.usage == 'customer')
        self.product_sale_qty = sum(quants.mapped('quantity'))
    
    @api.one
    @api.depends('product_sale_qty', 'product_qty')
    def _purchase_qty(self):
        self.product_purchase_qty = self.product_sale_qty + self.product_qty