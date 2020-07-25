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
    _name="report.custom_report.custom_report_template"#Respect naming format report.module_name.report_template_name
    _description="Custom report for TFC AGRO"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    def _get_sale_dayly_report(self):
        '''This method gets sale order by customer and by product'''
        #First we get all sale order for the giving date
        date = fields.Date.today()
        sales = self.env['sale.order'].search([('state', '=', 'sale')]).filtered(lambda line: fields.Date.to_date(line.confirmation_date) == date)
        sale_report = []
        for sale in sales:
            #get customer name
            customer_name = sale.partner_id.name
            sale_adl = sale.name
            if sale.payment_term_id:
                payment_term = sale.payment_term_id.name
            else:
                payment_term = ''
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
                    'payment_term' : payment_term,
                }
            sale_report.append(report_line)
        return sale_report
    
    def _get_stock_dayly_report(self):
        date = fields.Date.today()
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
    def _get_purchase_dayly_report(self):
        date = fields.Date.today()
        purchase_lines = []
        purchases = self.env['purchase.order'].search([('date_approve', '!=', False)]).filtered(lambda l : fields.Date.to_date(l.date_approve) == date)
        for purchase in purchases:
            vendor_name = purchase.partner_id.name
            payment_term = purchase.payment_term_id or False
            lines = purchase.order_line
            for line in lines:
                product_name = line.name
                product_uom = line.product_uom
                product_qty = line.product_qty
                unit_price= line.price_unit
                price_total = line.price_total
                currency = line.currency_id.name
                purchase_order = line.order_id
                purchase_line = {
                'vendor_name': vendor_name,
                'product_name': product_name,
                'product_uom': product_uom,
                'payment_term': payment_term_id,
                'product_qty': product_qty,
                'unit_price' : unit_price,
                'price_total' : price_total,
                'purchase_order': purchase_order
                }
                purchase_lines.append(purchase_line)
        return purchase_lines
    
    def _get_stock_aged(self):
        product = self.env['product.product'].search([('type', '=', 'product'), ('purchased_product_qty', '>=', 0)])
        product_ids = product.mapped('id')#Get only list of product id
        today = fields.Date.today()
        period = fields.Date.start_of(today, 'year')
        range_1 = period + timedelta(days=75)
        range_2 = period + timedelta(days=180)
        range_3 = period + timedelta(days=360)
        stock = []
        pattern_sl = '^PC/.+SL'
        pattern_dl = '^PC/.+DL'
        for product in product_ids:
            stock_move_75 = 0
            stock_move_180 = 0
            stock_move_360 = 0
            stock_move_360_plus = 0
            stock_in_75 = 0
            stock_in_180 = 0
            stock_in_360 = 0
            stock_in_360_plus = 0
            product_id = self.env['product.product'].search([('type', '=', 'product'), ('purchased_product_qty', '>=', 0), ('id', '=', product)])
            product_name = product_id.name            
            product_uom = product_id.uom_name
            #Get all stock move from starting period
            stock_move = self.env['stock.move'].search([('product_id.id', '=', product)])
            stock_rebag_plus = stock_move.filtered(lambda r : re.match(pattern_sl, r.name))
            stock_rebag_moins = stock_move.filtered(lambda r : re.match(pattern_dl, r.name))
            stock_in = self.env['stock.move'].search([('product_id.id', '=', product), ('picking_code', '=', 'incoming'), ('state', '=', 'done'), ('purchase_line_id', '!=', False)])
            stock_out = self.env['stock.move'].search([('product_id.id', '=', product), ('picking_code', '=', 'outgoing'), ('state', '=', 'done'), ('sale_line_id', '!=', False)])
            stock_mts = self.env['stock.move'].search([('product_id.id', '=', product), ('picking_code', '=', 'internal'), ('state', '=', 'done')])
            #-------------------------------0-75
            stock_in_75 = sum(stock_in.filtered(lambda l: fields.Date.to_date(l.date) >= period and fields.Date.to_date(l.date) < range_1).mapped('quantity_done'))
            stock_out_75 = sum(stock_out.filtered(lambda l: fields.Date.to_date(l.date) >= period and fields.Date.to_date(l.date) < range_1).mapped('quantity_done'))
            stock_rebag_75_plus = sum(stock_rebag_plus.filtered(lambda l: fields.Date.to_date(l.date) >= period and fields.Date.to_date(l.date) < range_1).mapped('quantity_done'))
            stock_rebag_75_moins = sum(stock_rebag_moins.filtered(lambda l: fields.Date.to_date(l.date) >= period and fields.Date.to_date(l.date) < range_1).mapped('quantity_done'))
            #-------------------------------------------75-180
            stock_in_180 = sum(stock_in.filtered(lambda l: fields.Date.to_date(l.date) >= range_1 and fields.Date.to_date(l.date) < range_2).mapped('quantity_done'))
            stock_out_180 = sum(stock_out.filtered(lambda l: fields.Date.to_date(l.date) >= range_1 and fields.Date.to_date(l.date) < range_2).mapped('quantity_done'))
            stock_rebag_180_plus = sum(stock_rebag_plus.filtered(lambda l: fields.Date.to_date(l.date) >= range_1 and fields.Date.to_date(l.date) < range_2).mapped('quantity_done'))
            stock_rebag_180_moins = sum(stock_rebag_moins.filtered(lambda l: fields.Date.to_date(l.date) >= range_1 and fields.Date.to_date(l.date) < range_2).mapped('quantity_done'))
            #-----------------------------------------180-360
            stock_in_360 = sum(stock_in.filtered(lambda l: fields.Date.to_date(l.date) >= range_2 and fields.Date.to_date(l.date) < range_3).mapped('quantity_done'))
            stock_out_360 = sum(stock_out.filtered(lambda l: fields.Date.to_date(l.date) >= range_2 and fields.Date.to_date(l.date) < range_3).mapped('quantity_done'))
            stock_rebag_360_plus = sum(stock_rebag_plus.filtered(lambda l: fields.Date.to_date(l.date) >= range_2 and fields.Date.to_date(l.date) < range_3).mapped('quantity_done'))
            stock_rebag_360_moins = sum(stock_rebag_moins.filtered(lambda l: fields.Date.to_date(l.date) >= range_2 and fields.Date.to_date(l.date) < range_3).mapped('quantity_done'))
            #-----------------------------------------------236+
            stock_in_360_plus = sum(stock_in.filtered(lambda l: fields.Date.to_date(l.date) >= range_3).mapped('quantity_done'))
            stock_out_360_plus = sum(stock_out.filtered(lambda l: fields.Date.to_date(l.date) >= range_3).mapped('quantity_done'))
            stock_rebag_plus_360_plus = sum(stock_rebag_plus.filtered(lambda l: fields.Date.to_date(l.date) >= range_3).mapped('quantity_done'))
            stock_rebag_moins_360_moins = sum(stock_rebag_moins.filtered(lambda l: fields.Date.to_date(l.date) >= range_3).mapped('quantity_done'))
            #range_3_plus
            if today > range_3:
                #stock 75
                stock_move_75 = stock_in_75 + stock_rebag_75_plus - stock_out_75 - stock_rebag_75_moins
                #stock 180
                stock_move_180 = stock_in_180 + stock_rebag_180_plus - stock_out_180 - stock_rebag_180_moins
                #stock 360
                stock_move_360 = stock_in_360 + stock_rebag_360_plus - stock_out_360 - stock_rebag_360_moins
                #stock 360 plus
                stock_move_360_plus = stock_in_360_plus + stock_rebag_plus_360_plus - stock_out_360_plus - stock_rebag_moins_360_moins

            if today <= range_3 and today > range_2:
                #stock 75
                stock_move_75 = stock_in_75 + stock_rebag_75_plus - stock_out_75 - stock_rebag_75_moins
                #stock 180
                stock_move_180 = stock_in_180 + stock_rebag_180_plus - stock_out_180 - stock_rebag_180_moins
                #stock 360
                stock_move_360 = stock_in_360 + stock_rebag_360_plus - stock_out_360 - stock_rebag_360_moins
                #stock 360 plus
                stock_move_360_plus = 0

            if today <= range_2 and today > range_1:
                #stock 75
                stock_move_75 = stock_in_75 + stock_rebag_75_plus - stock_out_75 - stock_rebag_75_moins
                #stock 180
                stock_move_180 = stock_in_180 + stock_rebag_180_plus - stock_out_180 - stock_rebag_180_moins
                #stock 360
                stock_move_360 = 0
                #stock 360 plus
                stock_move_360_plus = 0

            if today <= range_2 and today > range_1:
                #stock 75
                stock_move_75 = stock_in_75 + stock_rebag_75_plus - stock_out_75 - stock_rebag_75_moins
                #stock 180
                stock_move_180 = stock_in_180 + stock_rebag_180_plus - stock_out_180 - stock_rebag_180_moins
                #stock 360
                stock_move_360 = 0
                #stock 360 plus
                stock_move_360_plus = 0

            if today <= range_1 and today > period:
                #stock 75
                stock_move_75 = stock_in_75 + stock_rebag_75_plus - stock_out_75 - stock_rebag_75_moins
                #stock 180
                stock_move_180 = 0
                #stock 360
                stock_move_360 = 0
                #stock 360 plus
                stock_move_360_plus = 0
            stock_line = {
                'product_name': product_name,
                'product_uom': product_uom,
                'purchase_qty_75': stock_move_75,
                'purchase_qty_180': stock_move_180,
                'purchase_qty_360' : stock_move_360,
                'purchase_qty_360_plus' : stock_move_360_plus
            }
            stock.append(stock_line)
        return stock
    
    def _get_debtor_aged(self):
        today = fields.Date.today()
        period = fields.Date.start_of(today, 'year')
        days_24 = today - timedelta(days=24)
        days_30 = today + timedelta(days=30)
        days_37 = today + timedelta(days=37)
        days_45 = today + timedelta(days=45)
        days_60 = today + timedelta(days=60)
        days_90 = today + timedelta(days=90)
        debtor_report = []
        customer_ids = self.env['res.partner'].search([('customer', '=', True)]).mapped('id')
        for customer in customer_ids:
            customer_name = self.env['res.partner'].search([('customer', '=', True), ('id', '=', customer)]).name
            account_moves = self.env['account.move'].search([('partner_id.id', '=', customer), ('date', '>=', period)])
            amount_total = sum(account_moves.mapped('amount'))
            #amount < 24 days
            account_line = self.env['account.move.line'].search([])
            if today > days_90:
                amount_24 = sum(account_moves.filtered(lambda l: l.date <= days_24).mapped('amount'))
                amount_30 = sum(account_moves.filtered(lambda l: l.date > days_24 and l.date <= days_30).mapped('amount'))
                amount_37 = sum(account_moves.filtered(lambda l: l.date > days_30 and l.date <= days_37).mapped('amount'))
                amount_45 = sum(account_moves.filtered(lambda l: l.date > days_37 and l.date <= days_45).mapped('amount'))
                amount_60 = sum(account_moves.filtered(lambda l: l.date > days_45 and l.date <= days_60).mapped('amount'))
                amount_90 = sum(account_moves.filtered(lambda l: l.date > days_60 and l.date <= days_90).mapped('amount'))
                amount_90_plus = sum(account_moves.filtered(lambda l: l.date > days_90).mapped('amount'))
            
            elif today <= days_90 and today > days_60:
                amount_24 = sum(account_moves.filtered(lambda l: l.date <= days_24).mapped('amount'))
                amount_30 = sum(account_moves.filtered(lambda l: l.date > days_24 and l.date <= days_30).mapped('amount'))
                amount_37 = sum(account_moves.filtered(lambda l: l.date > days_30 and l.date <= days_37).mapped('amount'))
                amount_45 = sum(account_moves.filtered(lambda l: l.date > days_37 and l.date <= days_45).mapped('amount'))
                amount_60 = sum(account_moves.filtered(lambda l: l.date > days_60 and l.date <= days_90).mapped('amount'))
                amount_90 = sum(account_moves.filtered(lambda l: l.date > days_60 and l.date <= days_90).mapped('amount'))
                amount_90_plus = 0
            
            elif today <= days_60 and today > days_45:
                amount_24 = sum(account_moves.filtered(lambda l: l.date <= days_24).mapped('amount'))
                amount_30 = sum(account_moves.filtered(lambda l: l.date > days_24 and l.date <= days_30).mapped('amount'))
                amount_37 = sum(account_moves.filtered(lambda l: l.date > days_30 and l.date <= days_37).mapped('amount'))
                amount_45 = sum(account_moves.filtered(lambda l: l.date > days_37 and l.date <= days_45).mapped('amount'))
                amount_60 = sum(account_moves.filtered(lambda l: l.date > days_60 and l.date <= days_90).mapped('amount'))
                amount_90 = 0
                amount_90_plus = 0
                
            elif today <= days_45 and today > days_37:
                amount_24 = sum(account_moves.filtered(lambda l: l.date <= days_24).mapped('amount'))
                amount_30 = sum(account_moves.filtered(lambda l: l.date > days_24 and l.date <= days_30).mapped('amount'))
                amount_37 = sum(account_moves.filtered(lambda l: l.date > days_30 and l.date <= days_37).mapped('amount'))
                amount_45 = sum(account_moves.filtered(lambda l: l.date > days_37 and l.date <= days_45).mapped('amount'))
                amount_60 = 0
                amount_90 = 0
                amount_90_plus = 0
            
            elif today <= days_37 and today > days_30:
                amount_24 = sum(account_moves.filtered(lambda l: l.date <= days_24).mapped('amount'))
                amount_30 = sum(account_moves.filtered(lambda l: l.date > days_24 and l.date <= days_30).mapped('amount'))
                amount_37 = sum(account_moves.filtered(lambda l: l.date > days_30 and l.date <= days_37).mapped('amount'))
                amount_45 = 0
                amount_60 = 0
                amount_90 = 0
                amount_90_plus = 0
                
            elif today <= days_30 and today > days_24:
                amount_24 = sum(account_moves.filtered(lambda l: l.date <= days_24).mapped('amount'))
                amount_30 = sum(account_moves.filtered(lambda l: l.date > days_24 and l.date <= days_30).mapped('amount'))
                amount_37 = 0
                amount_45 = 0
                amount_60 = 0
                amount_90 = 0
                amount_90_plus = 0
            
            elif today <= days_24:
                amount_24 = sum(account_moves.filtered(lambda l: l.date <= days_24).mapped('amount'))
                amount_30 = 0
                amount_37 = 0
                amount_45 = 0
                amount_60 = 0
                amount_90 = 0
                amount_90_plus = 0
            
            debtor_report.append({
                'customer_name':customer_name,
                'amount_total': amount_total,
                'amount_24': amount_24,
                'amount_30': amount_30,
                'amount_37': amount_37,
                'amount_45': amount_45,
                'amount_60': amount_60,
                'amount_90': amount_90,
                'amount_90_plus': amount_90_plus
            })
        return debtor_report

    #Get creditor analysis
    def _get_creditor_analysis(self):
        today = fields.Date.today()
        period = fields.Date.start_of(today, 'year')
        days_90 = today - timedelta(days=90)
        days_180 = today + timedelta(days=180)
        days_365 = today + timedelta(days=365)
        creditor_report = []
        vendor_ids = self.env['res.partner'].search([('supplier', '=', True)]).mapped('id')
        for vendor in vendor_ids:
            vendor_name = self.env['res.partner'].search([('supplier', '=', True), ('id', '=', vendor)]).name
            account_moves = self.env['account.move'].search([('partner_id.id', '=', vendor), ('date', '>=', period)])
            amount_total = sum(account_moves.mapped('amount'))
            account_lines = self.env['account.move.line'].search([])
            if today > days_365:
                amount_90 = sum(account_moves.filtered(lambda a: a.date <= days_90).mapped('amount'))
                amount_180 = sum(account_moves.filtered(lambda a: a.date > days_90 and a.date <= days_180).mapped('amount'))
                amount_365 = sum(account_moves.filtered(lambda a: a.date > days_180 and a.date <= days_365).mapped('amount'))
                amount_365_plus = sum(account_moves.filtered(lambda a: a.date > days_365).mapped('amount'))
                
            elif today <= days_365 and today > days_180:
                amount_90 = sum(account_moves.filtered(lambda a: a.date <= days_90).mapped('amount'))
                amount_180 = sum(account_moves.filtered(lambda a: a.date > days_90 and a.date <= days_180).mapped('amount'))
                amount_365 = sum(account_moves.filtered(lambda a: a.date > days_180 and a.date <= days_365).mapped('amount'))
                amount_365_plus = 0
            
            elif today <= days_180 and today > days_90:
                amount_90 = sum(account_moves.filtered(lambda a: a.date <= days_90).mapped('amount'))
                amount_180 = sum(account_moves.filtered(lambda a: a.date > days_90 and a.date <= days_180).mapped('amount'))
                amount_365 = 0
                amount_365_plus = 0
            
            elif today <= days_90 :
                amount_90 = sum(account_moves.filtered(lambda a: a.date <= days_90).mapped('amount'))
                amount_180 = 0
                amount_365 = 0
                amount_365_plus = 0
            creditor_report.append(
                {
                'vendor_name': vendor_name,
                'amount_total' : amount_total,
                'amount_90': amount_90,
                'amount_180': amount_180,
                'amount_365': amount_365,
                'amount_365_plus': amount_365_plus
            })
        return creditor_report
    #Get security check
    def _get_pdc_security_check(self):
        date = fields.Date.today()
        security_check = []
        pdc_list = self.env['account.payment'].search([('payment_note', '=', 'security'), ('partner_type', '=', 'customer'), ('state', '!=', 'reconciled')]).filtered(lambda l:l.payment_date == date)
        for pdc in pdc_list:
            customer = pdc.partner_id.name
            client_bank = pdc.bank_reference
            cheque_reference = pdc.cheque_reference
            note = pdc.payment_note
            amount = pdc.amount
            pdc_line = {
                'customer_name' : customer,
                'client_bank' : client_bank,
                'check_number' : cheque_reference,
                'note': note,
                'amount': amount
            }
            security_check.append(pdc_line)
        return security_check
    
    #Get deposited check. check to deposit on a given date
    def _get_check_to_deposit(self):
        today = fields.Date.today()
        deposit_check = []
        pdc_list = self.env['account.payment'].search([('partner_type', '=', 'customer'), ('state', '!=', 'reconciled'),('payment_note', '=', 'deposited')]).filtered(lambda l:l.effective_date == date)
        for pdc in pdc_list:
            customer = pdc.partner_id.name
            client_bank = pdc.bank_reference
            cheque_reference = pdc.cheque_reference
            deposit_date = pdc.effective_date
            note = pdc.transaction_type
            amount = pdc.amount
            pdc_line = {
                'customer_name' : customer,
                'client_bank' : client_bank,
                'check_number' : cheque_reference,
                'deposit_date': deposit_date,
                'amount': amount
            }
            deposit_check.append(pdc_line)
        return deposit_check
    
    #Get check under clearance
    '''
    def _get_check_under_clearance(self):
        today = fields.Date.today()
        clearance_check = []
        check_ids = self.env['account.move.line'].search([('date', '=', date)]).mapped('check_deposit_id')
        for check in check_ids:
            if check.reconciled != False:
                payment_state = 'Paid'
            else:
                payment_state = 'Rejected'
            move_id = self.env['account.move.line'].search([('check_deposit_id', '=', check)]).move_id
            payment = self.env['account.payment'].search([('id', '=', check)])
            deposit = self.env['account.check.deposit'].search([('move_id', '=', move_id)])
            customer_name = payment.partner_id.name
            client_bank = payment.bank_reference
            cheque_reference = payment.check_reference
            bank_deposit = deposit.bank_journal_id.name
            amount = deposit.total_amount
            deposit_line = {
                'customer_name' : customer_name,
                'client_bank' : client_bank,
                'bank_deposit': bank_deposit,
                'cheque_reference' : cheque_reference,
                'date': date,
                'amount': amount,
                'payment_state': payment_state
            }
            clearance_check.append(pdc_line)
        return clearance_check
    '''
    '''
    def get_fund(self):
        fund_receive = []
        funds = self.env['account.payment'].search([('state', '=', 'reconciled')])
        for fund in funds:
            customer_name = fund.partner_id.name
            client_bank = fund.reference or 'Cash'
            cheque_reference = fund.cheque_reference or ''
            amount_receive = fund.amount
            payment_type = fund.payment_type
            deposit_id = self.env['account.move.line'].search([('payment_id.id', '=', fund)], limit=1).check_deposit_id.id
            bank_deposited = self.env['account.check.deposit'].search([('id', '=', deposit_id)]).bank_journal_id.name
            fund_line = {
                'customer_name': customer_name,
                'bank_deposited': bank_deposited,
                'client_bank' : client_bank,
                'cheque_reference': cheque_reference,
                'payment_type' : payment_type,
                'amount' : amount_receive
            }
        fund_receive.append(fund_line)
        return fund_receive
    '''
    @api.model
    def _get_report_values(self, docids, data=None):
        
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        date_to_obj = datetime.strptime(date_to, DATE_FORMAT).date()
        stock_dayly = self._get_stock_dayly_report()
        sale_dayly = self._get_sale_dayly_report()
        purchase_dayly = self._get_purchase_dayly_report()
        debtor_report = self._get_debtor_aged()
        stock_aged = self._get_stock_aged()
        creditor_report = self._get_creditor_analysis()
        security_check = self._get_pdc_security_check()
        deposit_check = self._get_check_to_deposit()
        docs = []
            
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],#self._name,#'create.custom.report', #model of the record
            'date_start':date_from,
            'date_end':date_to,
            'docs': docs,
            'stock': stock_dayly,
            'sale' : sale_dayly,
            'debtor_agewise':debtor_report,
            'stock_aged': stock_aged,
            'purchase' : purchase_dayly,
            'creditor_report': creditor_report,
            'security_check': security_check,
            'deposit_check' : deposit_check,
        }
    