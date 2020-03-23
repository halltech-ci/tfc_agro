# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import date_utils


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
    
    def _get_received_qty(self, product_id, date):
        moves = self.env['stock.move'].search([('picking_code', '=', 'incoming'), ('product_id.id', '=', product_id), ('product_type', '=', 'product')])#Get all incoming picking
        total_recept = 0.0
        total_transfert = 0.0
        for move in moves:
            if move.write_date.date() == date:
                if move.picking_code == 'incoming':
                    total_recept = total_recept + move.quantity_done
                if move.picking_code == 'internal':
                    total_transfert += total_transfert 
                total_recept = total_recept
                total_transfert = total_transfert
        return (total_recept, total_transfert)
    
    #Get rebaggage quantity per product
    def _get_rebaggage_qty(self, product_id, date):
        conversions = self.env['product.conversion'].search([('src_product_id.id', '=', product_id), ('state', '=', 'done')])
        rebaggage = 0.0
        for conversion in conversions:
            if conversion.date == date:
                rebaggage += conversion.qty_to_convert
            rebaggage = rebaggage
            return rebaggage
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        date_to_obj = datetime.strptime(date_to, DATE_FORMAT).date()
        #date = date_utils.to_date(date_to)
        
        docs = []
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
                'initial_qty': quant.qty_at_date + quant.sales_count - self._get_received_qty(quant.id, date_to_obj)[0],
                'recept_qty': self._get_received_qty(quant.id, date_to_obj)[0], #Qty of product recept in that day
                'internal_transfert': self._get_received_qty(quant.id, date_to_obj)[1],
                'rebaggage':  self._get_rebaggage_qty(quant.id, date_to_obj),
                #if 
            })
    
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],#self._name,#'create.custom.report', #model of the record
            'date_start':date_from,
            'date_end':date_to,
            'docs': docs,#
        }
    