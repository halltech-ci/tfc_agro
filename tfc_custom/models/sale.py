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


class SaleOrder(models.Model):
    _inherit='sale.order'
    
    
    vehicle_number=fields.Char(string='Vehicle Number')
    driver_name=fields.Char(string="Driver Name")
    driver_contacts=fields.Char(string="Driver Contact")
    customer_order_ref=fields.Char(string="Customer Order Ref")
    