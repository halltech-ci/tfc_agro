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
    filter_partner = True
    filter_all_entries = False
    
    '''_get_columns_name return a list of dict objects that reprsents header of the table for the report
    o- Each element of the list correspond to a column in the report.
    o- Each element must be a dict with the following keys:
        - Name (mandatory): the name that will be shown as a column header. key must be present but can have empty value
        - Class (optional): css class to add to the column
        - Style (optional): inline css style to add to the column
    '''
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
    
    """Group query  by order_id.
    options are define by filter define by user
    this method get list of all customer.
    """
    def _do_group_by_customer_id(self, options, line_id):
        sale_domain = [('state', 'in', ('sale'))]
        sql_query = """SELECT 
        """
        customers = self.env['sale.order.line'].search(sale_domain).mapped('order_partner_id') 
     
    
    
    
    '''This method sould return the list of lines of the report. The line_id parameter is set when unfolding a line in the report, in this 
    case this method should only return a subset of the line corresponding to line_id and domain
    o- The order of the list is the order in which the line will be display in the report.
    o- Each line of the list is a dictionary structure with specific keys.
    Dictionary for each line can contain the following information:
    o- id: id of the line. Referenced for footnote, unfolding, etc..
    o- name: what will be dysplay in the first column.
    o- colspan: use this if you want the colomn to span over many columns.
    o- columns: A list of column values
    o- class: css class to add to the row of the table
    o- unfoldable: True if the line can be unfolded
    o- unfolded: True if the line has already been unfolded
    o- parent_id: id of the parent line if this line is part of unfolded bloc.
    o- level: Determine the layout (should be beteween 0-9 or none)
    o- action_id: information passed to action
    o- caret_options: options that are displayed in dropdown for each line in report view (open invoice, open tax, annotate, etc.)
    
    '''
    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []
        #tables, where_clause, where_params = self.env['sale.order.line'].with_context(strict_range=True)._query_get()
        #user_type_id = self.env['account.account.type'].search([('type', '=', 'receivable')])
        context = self.env.context
        
        sql_query = """
        SELECT sum(\"sale_order_line\".price_total) AS total, p.id AS customer_id, p.name AS customer_name, so.id AS so_id, so.name AS so_name FROM "sale_order_line", "res_partner" AS p, "sale_order" AS so
        WHERE "sale_order_line".state IN ('sale') AND "sale_order_line".order_id = so.id AND so.partner_id = p.id
        GROUP BY p.id, so_id ORDER BY p.name
        """

        self.env.cr.execute(sql_query, [])
        results = self.env.cr.dictfetchall()
          
        sum_total = 0
        for line in results:
            #total += line.get('total')
            #product_uom = self.env['product.product'].search([('id', '=', line.get('product_uom'))]).uom_name
            #if self.env['stock.production.lot'].browse(line.get('lot_id')):
            #    product_lot = self.env['stock.production.lot'].browse(line.get('lot_id')).name
            #else:
            #    product_lot = ''
            #columns = [line.get('name'), product_uom, product_lot, line.get('payment_term'), line.get('product_uom_qty'), line.get('price_unit'), line.get('price_total'), line.get('so_name')]
            columns = ['', '', '', '', '', '',line.get('total'), line.get('so_name')]
            sum_total += line.get('total')
            lines.append({
                'id': line.get('customer_id'),
                'name': line.get('customer_name'),
                'level': 2,
                'unfoldable': False,
                #'unfolded': line_id == line.get('so_name') and True or False,
                'columns':[{'name': v} for v in columns],
            })
        lines.append({
            'id': 'total',
            'name': _('Total'),
            'level': 4,
            'colspan': 7,
            'class': 'total',
            'columns': [{'name': sum_total}]
            })

        return lines
                
    def _get_report_name(self):
        return _('Sale Report/partner')
        
    