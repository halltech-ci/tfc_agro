# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError
from odoo.addons.web.controllers.main import clean_action

class SaleCustomReports(models.AbstractModel):
    _name = "account.report.sale.custom.reports"
    _inherit = "account.report"
    _description = "hta sale custom report"
    
    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_all_entries = False
    
    def _get_columns_name(self, options):
        columns = [
            {'name': _('Customer')},
            {'name': _('Product')},
            {'name': _('Unit')},
            {'name': _('Lot')},
            {'name': _('Payment Terms')},
            {'name': _('Sold Qty'), 'class': 'number'},
            {'name': _('Unit Price'), 'class': 'number'},
            {'name': _('Price Total'), 'class': 'number'},
            {'name': _('ADL N°')}
        ]
        return columns
    
    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []
        #tables, where_clause, where_params = self.env['sale.order.line'].with_context(strict_range=True)._query_get()
        #user_type_id = self.env['account.account.type'].search([('type', '=', 'receivable')])
        
        sql_query = """
        SELECT "sale_order_line".id, "sale_order_line".name, "sale_order_line".lot_id, "sale_order_line".product_uom, "sale_order_line".product_uom_qty, "sale_order_line".price_unit, so.payment_term_id, p.id AS customer_id, p.name AS customer_name, so.id AS so_id, so.name AS so_name, "sale_order_line".price_total FROM "sale_order_line", "res_partner" AS p, "sale_order" AS so
        WHERE "sale_order_line".state IN ('sale') AND "sale_order_line".order_id = so.id AND so.partner_id = p.id
        GROUP BY p.name, p.id, so.id, "sale_order_line".id ORDER BY p.name
        """
        self.env.cr.execute(sql_query, [])
        results = self.env.cr.dictfetchall()
          
        total = 0
        for line in results:
            product_uom = self.env['product.product'].search([('id', '=', line.get('product_uom'))]).uom_name
            if self.env['stock.production.lot'].browse(line.get('lot_id')):
                product_lot = self.env['stock.production.lot'].browse(line.get('lot_id')).name
            else:
                product_lot = ''
            columns = [line.get('name'), product_uom, product_lot, line.get('payment_term'), line.get('product_uom_qty'), line.get('price_unit'), line.get('price_total'), line.get('so_name')]
            total += line.get('price_total')
            lines.append({
                'id': line.get('customer_id'),
                'name': line.get('customer_name'),
                'level': 2,
                'unfoldable': True,
                'columns':[{'name': v} for v in columns],
            })
        return lines
                
    def _get_report_name(self):
        return _('Sale Report/partner')
        
    