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
    
    def _get_sale_report(self, date):
        '''This method gets sale order by customer and by product'''
        #First we get all sale order for the giving date
        #sales = self.env['sale.order'].search([('state', '=', 'sale'), ('date', '=', date)])
        #date = fields.Date.today()
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
    
    def _get_stock_report(self, date):
        product_list = self.env['product.product'].search([('type', '=', 'product'), ('purchased_product_qty', '>=', 0)]).mapped('id')
        stock_position = []
        #date = fields.Date.today()
        for id in product_list:
            sale_qty_at_date = 0
            purchase_qty_at_date = 0
            rebaggage_plus_at_date = 0
            rebaggage_moins_at_date = 0
            internal_move_at_date = 0
            initial_stock = 0
            actual_stock = 0
            rebaggage_qty = 0
            pattern_sl = '^PC/.+SL'
            pattern_dl = '^PC/.+DL'
            pattern_inv = '^INV:'
            product_name = self.env['product.product'].search([('id', '=', id), ('type', '=', 'product'), ('purchased_product_qty', '>=', 0)]).name
            product_uom = self.env['product.product'].search([('id', '=', id), ('type', '=', 'product'), ('purchased_product_qty', '>=', 0)]).uom_name
            #actual_stock_qty = self.env['product.product'].search([('id', '=', id), ('type', '=', 'product'), ('purchased_product_qty', '>=', 0)]).qty_available
            moves = self.env['stock.move'].search([('product_id.id', '=', id)])#.filtered(lambda line: fields.Date.to_date(line.date) == date)
            if moves.exists():
                purchase = self.env['stock.move'].search([('product_id.id', '=', id), ('picking_code', '=','incoming'), ('state', '=', 'done'), ('purchase_line_id', '!=', False)])
                inventory = self.env['stock.move'].search([('product_id.id', '=', id), ('state', '=', 'done')]).filtered(lambda r : re.match(pattern_inv, r.name))
                receive = self.env['stock.move'].search([('product_id.id', '=', id), ('picking_code', '=','incoming'), ('state', '=', 'done')])
                sale = self.env['stock.move'].search([('product_id.id', '=', id), ('sale_line_id', '!=', False), ('picking_code', '=','outgoing'), ('state', '=', 'done')])
                internal_move = self.env['stock.move'].search([('product_id.id', '=', id), ('picking_code', '=','internal'), ('state', '=', 'done')])
                rebaggage_plus = moves.filtered(lambda r : re.match(pattern_sl, r.name))
                rebaggage_moins = moves.filtered(lambda r : re.match(pattern_dl, r.name))
                #actual_stock_qty = total_purchase - total_sale
                total_purchase = sum(purchase.filtered(lambda p : fields.Date.to_date(p.date) < date).mapped('quantity_done'))
                total_sale = sum(sale.filtered(lambda p : fields.Date.to_date(p.date) < date).mapped('quantity_done'))
                total_rebaggage_moins = sum(rebaggage_moins.filtered(lambda p : fields.Date.to_date(p.date) < date).mapped('quantity_done'))
                total_rebaggage_plus = sum(rebaggage_plus.filtered(lambda p : fields.Date.to_date(p.date) < date).mapped('quantity_done'))
                total_inv_qty = sum(inventory.filtered(lambda p : fields.Date.to_date(p.date) < date).mapped('quantity_done'))#qty for stock ajustement
                initial_stock = total_purchase - total_sale + total_inv_qty - total_rebaggage_moins + total_rebaggage_moins
                #today transaction
                if (sale.filtered(lambda s : fields.Date.to_date(s.date) == date)):
                    sale_qty_at_date = sum(sale.filtered(lambda s : fields.Date.to_date(s.date) == date).mapped('quantity_done'))

                if (purchase.filtered(lambda p : fields.Date.to_date(p.date)) == date):
                    purchase_qty_at_date = sum(purchase.filtered(lambda p : fields.Date.to_date(p.date) == date).mapped('quantity_done'))

                if (rebaggage_plus.filtered(lambda p : fields.Date.to_date(p.date) == date)):
                    rebaggage_plus_at_date = sum(rebaggage_plus.filtered(lambda p : fields.Date.to_date(p.date == date)).mapped('quantity_done'))
                if (rebaggage_moins.filtered(lambda p : fields.Date.to_date(p.date) == date)):
                    rebaggage_moins_at_date = sum(rebaggage_moins.filtered(lambda p : fields.Date.to_date(p.date) == date).mapped('quantity_done'))
                else:
                    rebaggage_moins_at_date = 0
                if (internal_move.filtered(lambda p : fields.Date.to_date(p.date) == date)):
                    internal_move_at_date = sum(internal_move.filtered(lambda p : fields.Date.to_date(p.date) == date).mapped('quantity_done'))

                actual_stock = initial_stock + purchase_qty_at_date - sale_qty_at_date - rebaggage_moins_at_date + rebaggage_plus_at_date
                rebaggage_qty = rebaggage_plus_at_date - rebaggage_moins_at_date 
                #actuel = initial + recu - vendu - converti ==> initial = actuel + vendu + converti - recu
            stock_position.append({
                'product_name':product_name,
                'product_uom':product_uom,
                'saled_qty': sale_qty_at_date,
                #'sale_reserved_qty' : sale_reserved_qty,
                'received_qty' : purchase_qty_at_date,
                'internal_move_qty' : internal_move_at_date,
                'rebaggage_qty' : rebaggage_qty,
                'actual_stock_qty' : actual_stock,
                'initial_stock_qty' : initial_stock,
            })
        return stock_position
    
    #All purchase qty for product in date range
    def _get_purchase_qty(self):
        product = self.env['product.product'].search([('type', '=', 'product'), ('purchased_product_qty', '>=', 0)])
        product_ids = product.mapped('id')#Get only list of product id
        today = fields.Date.today()
        period = fields.Date.start_of(today, 'year')
        range_1 = period + timedelta(days=75)
        range_2 = period + timedelta(days=180)
        range_3 = period + timedelta(days=360)
        purchase = []
        for product in product_ids:
            product_id = self.env['product.product'].search([('type', '=', 'product'), ('purchased_product_qty', '>=', 0), ('id', '=', product)])
            product_name = product_id.name
            product_uom = product_id.uom_name
            lines = self.env['purchase.order.line'].search([('state', '=', 'purchase'), ('product_id.id', '=', product)]).filtered(lambda l: fields.Date.to_date(l.date_order) >= period)
            #range_3_plus
            if today > range_3:
                purchase_qty_75 = sum((lines.filtered(lambda l: fields.Date.to_date(l.date_order) <= range_1)).mapped('product_qty'))
                purchase_qty_180 = sum((lines.filtered(lambda l: fields.Date.to_date(l.date_order) > range_1 and fields.Date.to_date(l.date_order) <= range_2)).mapped('product_qty'))
                purchase_qty_360 = sum((lines.filtered(lambda l: fields.Date.to_date(l.date_order) > range_2 and fields.Date.to_date(l.date_order) <= range_3)).mapped('product_qty'))
                purchase_qty_360_plus = sum((lines.filtered(lambda l: fields.Date.to_date(l.date_order) > range_3)).mapped('product_qty'))
            #range_3
            elif today <= range_3 and today > range_2:
                purchase_qty_75 = sum((lines.filtered(lambda l: fields.Date.to_date(l.date_order) <= range_1)).mapped('product_qty'))
                purchase_qty_180 = sum((lines.filtered(lambda l: fields.Date.to_date(l.date_order) > range_1 and fields.Date.to_date(l.date_order) <= range_2)).mapped('product_qty'))
                purchase_qty_360 = sum((lines.filtered(lambda l: fields.Date.to_date(l.date_order) > range_2 and fields.Date.to_date(l.date_order) <= range_3)).mapped('product_qty'))
                purchase_qty_360_plus = 0
            #range _2
            elif today <= range_2 and today > range_1:
                purchase_qty_75 = sum((lines.filtered(lambda l: fields.Date.to_date(l.date_order) <= range_1)).mapped('product_qty'))
                purchase_qty_180 = sum((lines.filtered(lambda l: fields.Date.to_date(l.date_order) >= range_1 and fields.Date.to_date(l.date_order) <= range_2)).mapped('product_qty'))
                purchase_qty_360 = 0
                purchase_qty_360_plus = 0
            #range_1
            elif today <= range_1:
                purchase_qty_75 = sum((lines.filtered(lambda l: fields.Date.to_date(l.date_order) <= range_1)).mapped('product_qty'))
                purchase_qty_180 = 0
                purchase_qty_360 = 0
                purchase_qty_360_plus = 0
            purchase_line = {
                'product_name': product_name,
                'product_uom': product_uom,
                'purchase_qty_75': purchase_qty_75,
                'purchase_qty_180': purchase_qty_180,
                'purchase_qty_360' : purchase_qty_360,
                'purchase_qty_360_plus' : purchase_qty_360_plus
            }
            purchase.append(purchase_line
            )
        return purchase
    
    def _get_debtor_agewise(self):
        today = fields.Date.today()
        customer_ids = self.env['res.partner'].search([('customer', '=', True)]).mapped('id')
        
        for customer in customer_ids:
            account_moves = self.env['account.move'].search([('parter_id.id', '=', customer)])
            account_line = self.env['account.move.line'].search([])
        #credit = 

    @api.model
    def _get_report_values(self, docids, data=None):
        
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        date_to_obj = datetime.strptime(date_to, DATE_FORMAT).date()
        stock = self._get_stock_report(date_to_obj)
        sale = self._get_sale_report(date_to_obj)
        purchase = self._get_purchase_qty()
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
    