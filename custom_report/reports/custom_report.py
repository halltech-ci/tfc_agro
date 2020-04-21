# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
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
    
    def _get_sale_report(self):
        '''This method gets sale order by customer and by product'''
        #First we get all sale order for the giving date
        #sales = self.env['sale.order'].search([('state', '=', 'sale'), ('date', '=', date)])
        date = fields.Date.today()
        sales = self.env['sale.order'].search([('state', '=', 'sale')]).filtered(lambda line: fields.Date.to_date(line.confirmation_date) == date)
        sale_report = []
        for sale in sales:
            #get customer name
            customer_name = sale.partner_id.name
            sale_adl = sale.name
            if sale.payment_term_id:
                sale_term = sale.payment_term_id.name
            else:
                sale_term = ''
            #Get order line information
            order_lines = sale.order_line
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
    
    def _get_stock_position_by_date(self):
        product_list = self.env['product.product'].search([('type', '=', 'product'), ('purchased_product_qty', '>=', 0)]).mapped('id')
        stock_position = []
        date = fields.Date.today()
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
            moves = self.env['stock.move'].search([('product_id.id', '=', id)]).filtered(lambda line: fields.Date.to_date(line.date) == date)
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
    
    def _get_date_range(self, start, end):
        '''
        Determine  la liste des dates entre 2 dates (debut, fin)
        '''
        if start > end :
            pass
        else:
            while start <= end:
                yield start
                start = start + timedelta(days=1)
        return start
    
    #All purchase qty for product in date range
    def _get_purchase_qty_history(self):
        product = self.env['product.product'].search([('type', '=', 'product'), ('purchased_product_qty', '>=', 0)])
        product_ids = product.mapped('id')#Get only list of product id
        today = fields.Date.today()
        start_of_period = fields.Date.start_of(today, 'year')
        date_range = self._get_date_range(start_of_period, today)
        range_list = [[0, 75], [75, 180], [181,360]]
        diff_date = (today - start_of_period).days#nomber of day since the beginning of the year.
        
        range_1 = start_of_period + timedelta(days=75)
        range_2 = start_of_period + timedelta(days=180)
        range_3 = start_of_period + timedelta(days=360)
        #get purchase order line by date
        purchase_qty = 0    
        purchase_position = []
        for product in product_ids:
            purchase_qty_75 = 0
            purchase_qty_180 = 0
            purchase_qty_360 = 0
            purchase_qty_360_plus = 0
            product_id = self.env['product.product'].search([('type', '=', 'product'), ('purchased_product_qty', '>=', 0), ('id', '=', product)])
            product_name = product_id.name
            product_uom = product_id.uom_name
            for date in date_range: #for every date in range i get purchase order line
                lines = self.env['purchase.order.line'].search([('state', '=', 'purchase'), ('product_id.id', '=', product)]).filtered(lambda l: fields.Date.to_date(l.date_order) == date)
                if lines.exists(): #if
                    for line in lines:
                        if date <= range_1:
                            purchase_qty_75 += line.product_qty
                        elif date <= range_2 and date > range_1:
                            purchase_qty_180 += line.product_qty
                        elif date > range_2 and date <= range_3:
                            purchase_qty_360 += line.product_qty
                        else:
                            purchase_qty_360_plus += line.product_qty
            purchase_position.append({
                'product_name': product_name,
                'product_uom': product_uom,
                'purchase_qty_75': purchase_qty_75,
                'purchase_qty_180': purchase_qty_180,
                'purchase_qty_360' : purchase_qty_360,
                'purchase_qty_360_plus' : purchase_qty_360_plus
                }
            )
        return purchase_position    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        date_to_obj = datetime.strptime(date_to, DATE_FORMAT).date()
        #date = date_utils.to_date(date_to)
        stock = self._get_stock_position_by_date()
        sale = self._get_sale_report()
        purchase = self._get_purchase_qty_history()
        docs = []
        #docs.append(stock_position)
        #docs.append(sale_report)
        #docs.append(purchase_report)
    
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],#self._name,#'create.custom.report', #model of the record
            'date_start':date_from,
            'date_end':date_to,
            'docs': docs,
            'stock': stock,
            'sale' : sale,
            'purchase' : purchase
        }
    