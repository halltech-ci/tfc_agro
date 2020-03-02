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


class StockPicking(models.Model):
    _inherit="stock.picking"
    
    driver_name = fields.Char(string='Driver Name', related = 'group_id.sale_id.driver_name')
    vehicle_number = fields.Char(string='Vehicle Number', related='group_id.sale_id.vehicle_number')
    driver_contacts = fields.Char(string="Driver Phone Number", related='group_id.sale_id.driver_contacts')
    driver_company = fields.Char(string="Driver Company")
    