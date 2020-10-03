# -*- coding: utf-8 -*-

import pytz
import time
from operator import itemgetter
from itertools import groupby
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date, timedelta
import re

class CustomReport(models.AbstractModel):
    _name="report.custom_report.custom_report_template"#Respect naming format report.module_name.report_template_name
    _description="Custom report for TFC AGRO"
    
    def _get_products(self, record):
        product_product_obj = self.env['product.product']
        domain = [('type', '=', 'product')]
        product_ids = False
        if record.category_ids:
            domain.append(('categ_id', 'in', record.category_ids.ids))
            product_ids = product_product_obj.search(domain)
        if record.product_ids:
            product_ids = record.product_ids
        if not product_ids:
             product_ids = product_product_obj.search(domain)
        return product_ids
    
    def get_location(self, records, warehouses=None):
        stock_ids = []
        location_obj = self.env['stock.location']
        domain = [('company_id', '=', records.company_id.id), ('usage', '=', 'internal')]
        if warehouses:
            for warehouse in warehouses:
                stock_ids.append(warehouse.view_location_id.id)
            domain.append(('location_id', 'child_of', stock_ids))
        elif records.warehouse_ids:
            for warehouse in records.warehouse_ids:
                stock_ids.append(warehouse.view_location_id.id)
            domain.append(('location_id', 'child_of', stock_ids))
        final_stock_ids = location_obj.search(domain).ids
        return final_stock_ids
    
    def convert_withtimezone(self, userdate):
        user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATETIME_FORMAT)
        tz_name = self.env.context.get('tz') or self.env.user.tz
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = user_date
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    
    
    def _get_beginning_inventory(self, record, product,warehouses=None):
        locations = [record.location_id.id] if record.location_id else self.get_location(record,warehouses)
        if isinstance(product, int):
            product_data = product
        else:
            product_data = product.id

        start_date = str(date.today()) if record.is_today_movement else str(record.start_date)
        from_date = self.convert_withtimezone(start_date + ' 00:00:00')
        self._cr.execute(''' 
                        SELECT id as product_id,coalesce(sum(qty), 0.0) as qty
                        FROM
                            ((
                            SELECT pp.id, pp.default_code,m.date,
                                CASE when pt.uom_id = m.product_uom 
                                THEN u.name 
                                ELSE (select name from uom_uom where id = pt.uom_id) 
                                END AS name,

                                CASE when pt.uom_id = m.product_uom
                                THEN coalesce(sum(-m.product_qty)::decimal, 0.0)
                                ELSE coalesce(sum(-m.product_qty * pu.factor / u.factor )::decimal, 0.0) 
                                END AS qty

                            FROM product_product pp 
                            LEFT JOIN stock_move m ON (m.product_id=pp.id)
                            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                            LEFT JOIN stock_location l ON (m.location_id=l.id)    
                            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                            LEFT JOIN uom_uom pu ON (pt.uom_id=pu.id)
                            LEFT JOIN uom_uom u ON (m.product_uom=u.id)
                            WHERE m.date <  %s AND (m.location_id in %s) AND m.state='done' AND pp.active=True AND pp.id = %s
                            GROUP BY  pp.id, pt.uom_id , m.product_uom ,pp.default_code,u.name,m.date
                            ) 
                            UNION ALL
                            (
                            SELECT pp.id, pp.default_code,m.date,
                                CASE when pt.uom_id = m.product_uom 
                                THEN u.name 
                                ELSE (select name from uom_uom where id = pt.uom_id) 
                                END AS name,
                                CASE when pt.uom_id = m.product_uom 
                                THEN coalesce(sum(m.product_qty)::decimal, 0.0)
                                ELSE coalesce(sum(m.product_qty * pu.factor / u.factor )::decimal, 0.0) 
                                END  AS qty
                            FROM product_product pp 
                            LEFT JOIN stock_move m ON (m.product_id=pp.id)
                            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                            LEFT JOIN stock_location l ON (m.location_dest_id=l.id)    
                            LEFT JOIN stock_picking p ON (m.picking_id=p.id)
                            LEFT JOIN uom_uom pu ON (pt.uom_id=pu.id)
                            LEFT JOIN uom_uom u ON (m.product_uom=u.id)
                            WHERE m.date < %s AND (m.location_dest_id in %s) AND m.state='done' AND pp.active=True AND pp.id = %s
                            GROUP BY  pp.id,pt.uom_id , m.product_uom ,pp.default_code,u.name,m.date
                            ))
                        AS foo
                        GROUP BY id
                    ''', (from_date, tuple(locations), product_data, from_date, tuple(locations), product_data))

        res = self._cr.dictfetchall()
        return res[0].get('qty', 0.00) if res else 0.00
    

    def get_product_move(self, record):
        domain = [('state', '=', 'done')]
        start_date = str(date.today()) if record.is_today_movement else str(record.start_date)
        end_date = str(date.today()) if record.is_today_movement else str(record.end_date)
        start_date += ' 00:00:00'
        end_date += ' 23:59:59'

        domain += [('date', '<=', end_date), ('date', '>=', start_date)]
        moves = self.env['stock.move.line'].search(domain).filtered(lambda l: l.move_id.product_type == 'product')
        sales_move = moves.filtered(lambda l : l.move_id.picking_code == 'outgoing' and len(l.move_id.sale_line_id) > 0)
        purchases_move = moves.filtered(lambda l : l.move_id.picking_code == 'incoming' and len(l.move_id.purchase_line_id) > 0)
        internal_move = moves.filtered(lambda l : l.move_id.picking_code == 'internal')
        #product_name=get('name'), product_qty=get('product_qty'), product_uom=get('product_uom')[1], partner_name=get('partner_id')[1], origin=get('') 
        product_move = {
            'sales_move': sales_move,
            'purchase_move': purchases_move,
            'internal_move': internal_move
            }
        return product_move
    
    #
    def _get_stock_aging(self, product):
        
        domain = [('state', '=', 'done'), ('product_id', '=', product)]
        stock_obj = self.env['stock.move.line'].search([])
        moves = stock_obj#self.env['stock.move.line'].search(domain)
        sales_move = moves.filtered(lambda l : l.move_id.picking_code == 'outgoing' and len(l.move_id.sale_line_id) > 0)
        purchases_move = moves.filtered(lambda l : l.move_id.picking_code == 'incoming' and len(l.move_id.purchase_line_id) > 0)
        period_interval = [0, 75, 180, 360]
        #[0-75]
        limit_0 = str(date.today() - timedelta(days=0)) + ' 23:59:00'
        limit_75 = str(date.today() - timedelta(days=75)) + ' 00:00:00'
        domain_0_75 = [('date', '<=', limit_0), ('date', '>', limit_75)] + domain
        stock_age_0_75 = sum(purchases_move.search(domain_0_75).mapped('qty_done'))# - sum(sales_move.search(domain_0_75).mapped('qty_done'))
        #[75-180]
        limit_180 = str(date.today() - timedelta(days=180)) + ' 00:00:00'
        domain_75_180 = [('date', '<=', limit_75), ('date', '>', limit_180)] + domain
        stock_age_75_180 = sum(purchases_move.search(domain_75_180).mapped('qty_done'))# - sum(sales_move.search(domain_75_180).mapped('qty_done'))
        #[180-360]
        limit_360 = str(date.today() - timedelta(days=360)) + ' 00:00:00'
        domain_180_360 = [('date', '<=', limit_180), ('date', '>', limit_360)] + domain
        stock_age_180_360 = sum(purchases_move.search(domain_180_360).mapped('qty_done'))# - sum(sales_move.search(domain_180_360).mapped('qty_done'))
        #[360+]
        limit_360 = str(date.today() - timedelta(days=75)) + ' 00:00:00'
        domain_360 = [('date', '<=', limit_360)] + domain
        stock_age_360 = sum(purchases_move.search(domain_360).mapped('qty_done'))# - sum(sales_move.search(domain_360).mapped('qty_done'))
        res = {
            'stock_age_0_75':stock_age_0_75,
            'stock_age_75_180': stock_age_75_180,
            'stock_age_180_360': stock_age_180_360,
            'stock_age_360': stock_age_360
        }
        return res
    
    def get_stock_agewise(self, product):
        total_sales = 0.0
        total_purchases = 0.0
        period_list = [75, 180, 360]
        today = str(date.today()) + ' 00:00:00'
        periods = [(0, today)]
        begin = 1
        i = 0
        res = []
        domain = [('state', '=', 'done'), ('product_id', '=', product)]
        stock_obj = self.env['stock.move.line'].search(domain)
        moves = self.env['stock.move.line'].search(domain).filtered(lambda l: l.move_id.product_type == 'product')
        sales_move = moves.filtered(lambda l : l.move_id.picking_code == 'outgoing' and len(l.move_id.sale_line_id) > 0)
        purchases_move = moves.filtered(lambda l : l.move_id.picking_code == 'incoming' and len(l.move_id.purchase_line_id) > 0)
        for period in period_list:
            limit_period = str(date.today() - timedelta(days=period)) + ' 00:00:00'
            range_name = [begin, period]
            begin = period_list[i] + 1
            i += 1
            tranche = '{0}'.format(range_name), limit_period
            
            domain = [('date', '<=', limit_period)]
            periods.append(tranche)
            #[('(1, 24)', '2020-07-06 00:00:00'), ('(25, 30)', '2020-06-30 00:00:00'), ('(31, 37)', '2020-06-23 00:00:00'), ('(38, 45)', '2020-06-15 00:00:00'), ('(46, 60)', '2020-05-31 00:00:00')]
        period_length = len(periods)
        for l in range(1, period_length):
            name = periods[l][0]
            end = periods[l][1]
            start = periods[l-1][1]
            domain = [('date', '<', start), ('date', '>=', end)]
            total_sales = sum(sales_move.search(domain).mapped('qty_done'))
            total_purchases = sum(purchases_move.search(domain).mapped('qty_done'))
            stock_age = total_purchases #- total_sales
            stock_values = (name, stock_age)
            res.append(stock_values)
        resultat = res
        return resultat    
    
    def _get_debtor_age(self, partner):
        user_type_id = self.env['account.account.type'].search([('type', '=', 'receivable')])
        #where_params = []
        #where_clause = 'AND ' + where_clause
        '''sql = """
            SELECT sum(aml.balance) AS balance, p.id, p.name AS partner_name 
            FROM account_move_line aml, res_partner p
            WHERE aml.invoice_id IS NOT NULL AND aml.partner_id=p.id AND aml.user_type_id = %s """'AND' +where_params+"""
            GROUP BY p.id
            """ '''
        #params = [user_type_id.id] + where_params
        #self.env.cr.execute(sql, params)
        #results = self.env.cr.dictfetchall()
        
        #domain = [('partner_id', '=', partner)]
        domain = [('user_type_id', '=', user_type_id.id), ('partner_id', '=', partner), ('invoice_id', '!=', False)]
        req = self.env['account.move.line']
        debtor_balance = req
        debtor_0_24 = 0.0
        debtor_24_30 = 0.0
        debtor_30_45 = 0.0
        debtor_45_60 = 0.0
        debtor_60_90 = 0.0
        debtor_90 = 0.0
        amount = 0.0
        #creditor_balance = sum(req.filtered(lambda aml: aml.user_type_id.type == 'payable').mapped('balance'))
        #period = [0, 24, 30, 45, 60, 90]
        #0->24
        limit_0 = str(date.today() - timedelta(days=0))# + ' 23:59:00'
        limit_24 = str(date.today() - timedelta(days=24))# + ' 00:00:00'
        domain_0_24 = [('date', '<=', limit_0), ('date', '>', limit_24)] + domain
        where_param_0_24 = 'aml.date <= '  
        debtor_0_24 = sum(debtor_balance.search(domain_0_24).mapped('balance'))
        #24->30
        limit_30 = str(date.today() - timedelta(days=30))# + ' 00:00:00'
        domain_24_30 = [('date', '<=', limit_24), ('date', '>', limit_30)] + domain
        debtor_24_30 = sum(debtor_balance.search(domain_24_30).mapped('balance'))
        #30->45
        limit_45 = str(date.today() - timedelta(days=45))# + ' 00:00:00'
        domain_30_45 = [('date', '<=', limit_30), ('date', '>', limit_45)] + domain
        debtor_30_45 = sum(debtor_balance.search(domain_30_45).mapped('balance'))
        #45->60
        limit_60 = str(date.today() - timedelta(days=60))# + ' 00:00:00'
        domain_45_60 = [('date', '<=', limit_45), ('date', '>', limit_60)] + domain
        debtor_45_60 = sum(debtor_balance.search(domain_45_60).mapped('balance'))
        #60->90
        limit_90 = str(date.today() - timedelta(days=90))# + ' 00:00:00'
        domain_60_90 = [('date', '<=', limit_60), ('date', '>', limit_90)] + domain
        debtor_60_90 = sum(debtor_balance.search(domain_60_90).mapped('balance'))
        #90->+
        domain_90 = [('date', '<=', limit_90)] + domain
        debtor_90 = sum(debtor_balance.search(domain_90).mapped('balance'))
        amount = debtor_0_24 + debtor_24_30 + debtor_30_45 + debtor_45_60 + debtor_60_90 + debtor_90
        res = {
            'amount': amount,
            'debtor_0_24': debtor_0_24,
            'debtor_24_30': debtor_24_30,
            'debtor_30_45': debtor_30_45,
            'debtor_45_60': debtor_45_60,
            'debtor_60_90': debtor_60_90,
            'debtor_90': debtor_90
        }
        
        return res
    
    #Creditor analysis
    def _get_creditor_age(self, partner):
        user_type_id = self.env['account.account.type'].search([('type', '=', 'payable')])
        #where_params = []
        #where_clause = 'AND ' + where_clause
        '''sql = """
            SELECT sum(aml.balance) AS balance, p.id, p.name AS partner_name 
            FROM account_move_line aml, res_partner p
            WHERE aml.invoice_id IS NOT NULL AND aml.partner_id=p.id AND aml.user_type_id = %s """'AND' +where_params+"""
            GROUP BY p.id
            """ '''
        #params = [user_type_id.id] + where_params
        #self.env.cr.execute(sql, params)
        #results = self.env.cr.dictfetchall()
        
        #domain = [('partner_id', '=', partner)]
        domain = [('user_type_id', '=', user_type_id.id), ('partner_id', '=', partner), ('invoice_id', '!=', False)]
        req = self.env['account.move.line']
        creditor_balance = req
        creditor_0_90 = 0.0
        creditor_90_180 = 0.0
        creditor_180_365 = 0.0
        creditor_365 = 0.0
        amount = 0.0
        #creditor_balance = sum(req.filtered(lambda aml: aml.user_type_id.type == 'payable').mapped('balance'))
        #period = [0, 24, 30, 45, 60, 90]
        #0->24
        limit_0 = str(date.today() - timedelta(days=0))# + ' 23:59:00'
        limit_90 = str(date.today() - timedelta(days=90))# + ' 00:00:00'
        domain_0_90= [('date', '<=', limit_0), ('date', '>', limit_90)] + domain
        creditor_0_90 = sum(creditor_balance.search(domain_0_90).mapped('balance'))
        #24->30
        limit_180 = str(date.today() - timedelta(days=180))# + ' 00:00:00'
        domain_90_180 = [('date', '<=', limit_90), ('date', '>', limit_180)] + domain
        creditor_90_180 = sum(creditor_balance.search(domain_90_180).mapped('balance'))
        #30->45
        limit_365 = str(date.today() - timedelta(days=365))# + ' 00:00:00'
        domain_180_365 = [('date', '<=', limit_180), ('date', '>', limit_365)] + domain
        creditor_180_365 = sum(creditor_balance.search(domain_180_365).mapped('balance'))
        #365->+
        domain_365 = [('date', '<=', limit_365)] + domain
        creditor_365 = sum(creditor_balance.search(domain_365).mapped('balance'))
        amount = creditor_0_90 + creditor_90_180 + creditor_180_365 + creditor_365
        res = {
            'amount': amount,
            'creditor_0_90': creditor_0_90,
            'creditor_90_180': creditor_90_180,
            'creditor_180_365': creditor_180_365,
            'creditor_365': creditor_365,
        }
        
        return res

    def _get_check_status(self, record):
        start_date = str(record.start_date)
        end_date = str(record.end_date)
        company = record.company_id
        check_account = company.check_on_hand_journal
        
        domain = [('date', '>=', start_date), ('date', '<=', end_date)]
        deposit_domain = [('check_deposit_id', '!=', False)] + domain
        move_domain = [('account_id', '=', check_account.id)] + domain
        check_domain = [('check_deposit_id', '=', False), ('account_id', '=', check_account.id)] + domain
        move_line = self.env['account.move.line'].search(domain)
        partners = move_line.search(move_domain).mapped('partner_id')
        deposits = move_line.search(deposit_domain)
        checks = move_line.search(check_domain)
        res = {
            'partner': partners,
            "check": checks,
            'deposit': deposits
        }
        return res
    
    
    #mis for payment and check
    def _get_payment_data(self, record):
        start_date = str(record.start_date)
        company = record.company_id#self.env['res.company']._company_default_get()
        pdc_account_id = company.pdc_check_account.id
        check_on_hand_account_id = company.check_on_hand_journal.id
        check_on_bank_account_id = company.check_on_bank_journal.id
        domain = [('payment_date', '=', start_date), ('partner_type', '=', 'customer')]
        pdc_ids = self.env['account.payment.method'].search([('code', '=', 'pdc')])
        #check_on_hand_account = self.env['account.account'].search([('code', '=like', '5130%')], limit=1)
        #check_on_bank_account = self.env['account.account'].search([('code', '=like', '5140%')], limit=1)
        payment = self.env['account.payment']
        
        #pdc_domain = [('payment_method_code', '=', 'pdc')] + domain
        #reconcile payment
        reconcile_domain = [('state', '=', 'reconciled')] + domain
        pdc_domain = [('journal_id.default_debit_account_id', '=', pdc_account_id)] + domain
        res = payment.search(reconcile_domain)
        check_on_bank_domain = [("journal_id.default_debit_account_id", "=", check_on_bank_account_id)] + domain
        check_on_hand_domain = [("journal_id.default_debit_account_id", "=", check_on_hand_account_id)] + domain
        pdc_check = payment.search(pdc_domain)
        check_on_bank = payment.search(check_on_bank_domain)
        check_on_hand = payment.search(check_on_hand_domain)
        reconciled_check = payment.search(reconcile_domain)
        
        res = {
            'pdc_check': pdc_check,
            'check_on_bank': check_on_bank,
            'check_on_hand': check_on_hand,
            'reconciled_check': reconciled_check
        }

        return res
    
    
    def get_product_sale_qty(self, record, product=None,warehouses=None):
        if not product:
            product = self._get_products(record)
        if isinstance(product, list):
            product_data = tuple(product)
        else:
            product_data = tuple(product.ids)

        if product_data:
            locations = [record.location_id.id] if record.location_id else self.get_location(record, warehouses)
            start_date = str(date.today()) if record.is_today_movement else str(record.start_date)
            end_date = str(date.today()) if record.is_today_movement else str(record.end_date)

            start_date += ' 00:00:00'
            end_date += ' 23:59:59'
            #product_qty_out = 
            self._cr.execute('''
                            SELECT pp.id AS product_id,pt.categ_id,
                                sum((
                                CASE WHEN spt.code in ('outgoing') AND sm.location_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory'
                                THEN -(sm.product_qty * pu.factor / pu2.factor)
                                ELSE 0.0 
                                END
                                )) AS product_qty_out,
                                 sum((
                                CASE WHEN spt.code in ('incoming') AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                                THEN (sm.product_qty * pu.factor / pu2.factor) 
                                ELSE 0.0 
                                END
                                )) AS product_qty_in,

                                sum((
                                CASE WHEN (spt.code ='internal' OR spt.code is null) AND sm.location_dest_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                                THEN (sm.product_qty * pu.factor / pu2.factor)  
                                WHEN (spt.code ='internal' OR spt.code is null) AND sm.location_id in %s AND sourcel.usage !='inventory' AND destl.usage !='inventory' 
                                THEN -(sm.product_qty * pu.factor / pu2.factor) 
                                ELSE 0.0 
                                END
                                )) AS product_qty_internal,

                                sum((
                                CASE WHEN sourcel.usage = 'inventory' AND sm.location_dest_id in %s  
                                THEN  (sm.product_qty * pu.factor / pu2.factor)
                                WHEN destl.usage ='inventory' AND sm.location_id in %s 
                                THEN -(sm.product_qty * pu.factor / pu2.factor)
                                ELSE 0.0 
                                END
                                )) AS product_qty_adjustment
                            FROM product_product pp 
                            LEFT JOIN  stock_move sm ON (sm.product_id = pp.id and sm.date >= %s and sm.date <= %s and sm.state = 'done' and sm.location_id != sm.location_dest_id)
                            LEFT JOIN stock_picking sp ON (sm.picking_id=sp.id)
                            LEFT JOIN stock_picking_type spt ON (spt.id=sp.picking_type_id)
                            LEFT JOIN stock_location sourcel ON (sm.location_id=sourcel.id)
                            LEFT JOIN stock_location destl ON (sm.location_dest_id=destl.id)
                            LEFT JOIN uom_uom pu ON (sm.product_uom=pu.id)
                            LEFT JOIN uom_uom pu2 ON (sm.product_uom=pu2.id)
                            LEFT JOIN product_template pt ON (pp.product_tmpl_id=pt.id)
                            WHERE pp.id in %s
                            GROUP BY pt.categ_id, pp.id order by pt.categ_id
                            ''', (tuple(locations), tuple(locations), tuple(locations), tuple(locations), tuple(locations), tuple(locations), start_date, end_date, product_data))
            values = self._cr.dictfetchall()
            #values = {'product_id': id, 'categ_id': categ_id, 'product_qty_out': categ_id, 'product_qty_out': qty_out, 'product_qty_in': qty_in, 'product_qty_internal': qty_int, 'prduct_qty_adjustment': qty_adj}
            if record.group_by_categ:
                sort_by_categories = sorted(values, key=itemgetter('categ_id'))
                records_by_categories = dict((k, [v for v in itr]) for k, itr in groupby(sort_by_categories, itemgetter('categ_id')))
                if not record.with_zero:
                    today_record_by_cat = {}
                    for key, value in records_by_categories.items():
                        for each in value:
                            product_beg_qty = self._get_beginning_inventory(record, each['product_id'])
                            today_movment_total = each.get('product_qty_in') + each.get('product_qty_internal') + each.get('product_qty_adjustment') + each.get('product_qty_out')
                            if record.is_today_movement:
                                if today_movment_total != 0:
                                    if key not in today_record_by_cat:
                                        today_record_by_cat.update({key:[each]})
                                    else:
                                        today_record_by_cat[key] += [each]
                            elif (product_beg_qty + today_movment_total) != 0:
                                if key not in today_record_by_cat:
                                    today_record_by_cat.update({key:[each]})
                                else:
                                    today_record_by_cat[key] += [each]
                    return today_record_by_cat
                else:
                    return records_by_categories
            else:
                return values[0]


    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('custom_report.custom_report_template')
        record_id = data['form']['id'] if data and data.get('form', False) and data.get('form').get('id', False) else docids[0]
        records = self.env['create.custom.report'].browse(record_id)
        docids = records.ids
        res = {
           'doc_model': report.model,
           'doc_ids': docids,
           'docs': records,
           'data': data,
           'lang': "fr_FR",
           'get_beginning_inventory': self._get_beginning_inventory,
           'get_products':self._get_products,
           'get_product_sale_qty':self.get_product_sale_qty,
           'get_location':self.get_location(records),
           #'product_uom': self._get_product_uom,
           'get_product_move': self.get_product_move,
           'get_stock_agewise': self._get_stock_aging,
           'debtor_age': self._get_debtor_age,
           'creditor_age': self._get_creditor_age,
           'get_payments': self._get_payment_data,
           'get_checks': self._get_check_status
        }
        return res

    