# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import date_utils
import re

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
    
    def _get_sale_report(self, date):
        '''This method gets sale order by customer and by product'''
        #First we get all sale order for the giving date
        sales = self.env['sale.order'].search([('type_name', '=', 'Sales Order'), ('date', '=', date)])
        sale_report = []
        for sale in sales:
            #get customer name
            customer_name = sale.partner_id.name
            sale_adl = sale.name
            if sale.payment_term_id:
                sale_term = sale.payment_term_id
            else:
                sale_term = ''
            #Get order line information
            order_lines = self.env['sale.order.line'].search([('order_id.id', '=', sale.id)])
            for order_line in order_lines:
                if order_line.lot_id:
                    product_lot = order_line.lot_id.name
                else:
                    product_lot = ''
                report_line = {
                    'product_id':order_line.product_id.name,
                    'sale_qty' : order_line.product_uom_qty,
                    'unit_price' : order_line.price_unit,
                    'product_uom' : order_line.product_uom.name,
                    'product_lot' : product_lot,
                    'price_total' : order_line.price_total,
                    'customer_name' : customer_name,
                    'sale_adl' : sale_adl,
                    'sale_term' : sale_term,
                }
                sale_report.append(report_line)
        return sale_report
    
    def _get_stock_position_by_date(self, date):
        products = self.env['product.product'].search([('type', '=', 'product'), ('purchased_product_qty', '>=', 0)])
        product_ids = []
        for product in products:
            product_ids.append(product.id)
        product_list = product_ids
        
        stock_position = []
        for id in product_list:
            saled_qty = 0
            sale_reserved_qty = 0
            purchase_reserved_qty = 0
            received_qty = 0
            internal_move_qty = 0
            rebaggage_qty = 0
            rebaggage_out = 0
            rebaggage_in = 0
            product_name = self.env['product.product'].search([('id', '=', id), ('type', '=', 'product'), ('purchased_product_qty', '>=', 0)]).name
            product_uom = self.env['product.product'].search([('id', '=', id), ('type', '=', 'product'), ('purchased_product_qty', '>=', 0)]).uom_name
            actual_stock_qty = self.env['product.product'].search([('id', '=', id), ('type', '=', 'product'), ('purchased_product_qty', '>=', 0)]).qty_available
            moves = self.env['stock.move'].search([('product_id.id', '=', id), ('move_date', '=', date)])
            '''
            conversions = self.env['product.conversion'].search([('src_product_id', '=', id), ('state', '=', 'done')])
            if conversions.exists():
                for conversion in conversions:
                    rebaggage_qty = conversion.qty_to_convert
            '''
            if moves.exists():
                for move in moves:
                    pattern_sl = '^PC/.+SL'
                    pattern_dl = '^PC/.+DL'
                    if re.match(pattern_sl, move.name):
                        rebaggage_out += move.quantity_done
                    if re.match(pattern_dl, move.name):
                        rebaggage_in += move.quantity_done
                    if move.sale_line_id and move.picking_code == 'outgoing' and move.state=='done':
                        saled_qty += move.quantity_done
                    #Compute reserved qty
                    if move.sale_line_id and move.picking_code == 'outgoing' and move.state=='assigned':
                        sale_reserved_qty += move.reserved_availability
                    #compute received quantity
                    if move.purchase_line_id and move.picking_code == 'incoming' and move.state=='done':
                        received_qty += move.quantity_done
                    #Compute purchase reserved
                    if move.purchase_line_id and move.picking_code == 'incoming' and move.state=='assigned':
                        purchase_reserved_qty += move.quantity_done
                    #compute internal transfert quantity
                    if move.picking_code == 'internal' and move.state=='done':
                        internal_move_qty += move.quantity_done
            rebaggage_qty = rebaggage_out #+ rebaggage_in
            initial_stock_qty = actual_stock_qty - received_qty + saled_qty + rebaggage_qty
            #actuel = initial + recu - vendu - converti ==> initial = actuel + vendu + converti - recu
            stock_position.append({
                'product_name':product_name,
                'product_uom':product_uom,
                'saled_qty': saled_qty,
                'sale_reserved_qty' : sale_reserved_qty,
                'received_qty' : received_qty,
                'internal_move_qty' : internal_move_qty,
                'rebaggage_qty' : rebaggage_qty,
                'actual_stock_qty' : actual_stock_qty,
                'initial_stock_qty' : initial_stock_qty,
            })
        return stock_position
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        date_to_obj = datetime.strptime(date_to, DATE_FORMAT).date()
        #date = date_utils.to_date(date_to)
        stock_position = self._get_stock_position_by_date(date_to_obj)
        sale_report = self._get_sale_report(date_to_obj)
        docs = []
        docs.append(stock_position)
        docs.append(sale_report)
    
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],#self._name,#'create.custom.report', #model of the record
            'date_start':date_from,
            'date_end':date_to,
            'docs': docs,#
        }
    