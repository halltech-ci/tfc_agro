# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, date_utils


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

class CustomReport(models.AbstractModel):
    _name="report.tfc_custom.custom_report_template"#Respect naming format report.module_name.report_template_name
    _description="Custom report for TFC AGRO"
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        
        docs = []
        #stock.quant give product quantity in on hands at any time
        #ref_datetime = date_utils.datetime(date_from, 'day')#Get date initial datetime
        #quants_from = self.env['product.product'].search([('type', '=', product), ('write_date', '<=', ref_datetime)])
        #quants_to = self.env['product.product'].search([('type', '=', product), ('write_date', '>=', date_to)])
        quants = self.env['product.product'].search([('type', '=', 'product')])
        #accountmove_line = self.env['account.move.line'].search([()])
        for quant in quants :
            docs.append({
                'product': quant.code,
                'product_uom': quant.uom_name,
                'product_qty': quant.qty_at_date,
                #'product_lot': quant.lot_id,
                'sale_qty': quant.sales_count,
                'purchase_qty' : quant.purchased_product_qty,#Total qty purchased for this product
                'delivery_order': quant.outgoing_qty, #qty waiting for delivery
                'recept_order': quant.incoming_qty, #qty purchase and waiting for reception
                'virtual_available': quant.virtual_available, #forcasted (prevision) qty
                'initial_qty': quant.qty_at_date + quant.sales_count,
                'recept_qty':0, #Qty of product recept in that day
                #if 
            })
    
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],#self._name,#'create.custom.report', #model of the record
            'date_start':date_from,
            'date_end':date_to,
            'docs': docs,#
        }
    