# -*- coding: utf-8 -*-

import time
from odoo import api, models, fields, _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError
from odoo.addons.web.controllers.main import clean_action

from datetime import datetime, date
from odoo.tools.misc import format_date

class SaleCustomReports(models.AbstractModel):
    _name = "account.report.sale.custom.reports"
    _inherit = "account.report"
    _description = "hta sale custom report"
    
    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    #filter_partner = True
    #filter_all_entries = False
    
    '''_get_columns_name return a list of dict objects that reprsents header of the table for the report
    o- Each element of the list correspond to a column in the report.
    o- Each element must be a dict with the following keys:
        - Name (mandatory): the name that will be shown as a column header. key must be present but can have empty value
        - Class (optional): css class to add to the column
        - Style (optional): inline css style to add to the column
    '''
    def _get_columns_name(self, options):
        columns = [
            {},
            {'name': _('Product'), 'class': 'text-right'},
            {'name': _('Unit'), 'class': 'text-right'},
            {'name': _('Vessel'), 'class': 'text-right'},
            {'name': _('Payment Terms'), 'class': 'text-right'},
            {'name': _('Sold Qty'), 'class': 'number'},
            {'name': _('Unit Price'), 'class': 'number'},
            {'name': _('Price Total'), 'class': 'number'},
            {'name': _('ADL N°'), 'class': 'text-right'}
        ]
        return columns
    
    #Get options in context
    def _set_context(self, options):
        ctx = super(SaleCustomReports, self)._set_context(options)
        ctx['strict_range'] = True
        return ctx
    
    
    """
    Context
    ---------
    The context is a python dictionary and is used to pass certain data to a method. Since nearly all methods have a context parameter you can use the context to pass data through several levels of python methods. For example you can set a context value in a XML-view and process it in the write() method of the osv object.
    """
    def _get_filters_otions(self, options):
            
        if options['date'].get('date_from'):
            date_from = options['date'].get('date_from')
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
        context = self.env.context
        #partners = []
        domain = [('state', '=', 'sale')]
        
        date_from = options['date'].get('date_from')
        date_to = options['date'].get('date_to')
        date_from_datetime = fields.Datetime.from_string(date_from)
        date_to_datetime = fields.Datetime.from_string(date_to)
        domain=[('date_order', '>=', date_from_datetime), ('date_order', '<=', date_to_datetime)] + domain
    

        if line_id != None:
            domain = [('order_partner_id', '=', line_id)] + domain
            unfold_query = self.env['sale.order.line'].with_context(strict_range=True).search_read(domain)
            #res = self.
        
        orm_query = self.env['sale.order.line'].with_context(strict_range=True).read_group(domain, ['price_total:sum','order_partner_id', 'order_id'], ['order_partner_id'], ['order_partner_id'])
        

        #self.env.cr.execute(sql_query, [])
        #results = self.env.cr.dictfetchall()
        total = 0
        for line in orm_query:
            columns = ['', '', '', '', '', '',line.get('price_total'), '']
            total += line.get('price_total')
            partner_name = self.env['res.partner'].browse(line.get('order_partner_id')[0]).name
            lines.append({
                'id': line.get('order_partner_id')[0],
                'name': partner_name,
                'level': 2,
                'unfoldable': True,
                'unfolded': line_id == line.get('order_partner_id') and True or False,
                'columns':[{'name': v} for v in columns],
            })
        #Adding sale orders lines
        if line_id :
            for child_line in unfold_query:
                columns = [child_line.get('name'), child_line.get('product_uom')[1], child_line.get('lot_id'), child_line.get('payment_term'), child_line.get('product_uom_qty'), child_line.get('price_unit'), child_line.get('price_total'), child_line.get('order_id')[1]]
                lines.append({
                    'id': child_line.get('id'),
                    'name': format_date(self.env, child_line.get('date_order')),
                    'class': 'date',
                    'level': 4,
                    'parent_id' : line_id,
                    'columns': [{'name': v} for v in columns],
                })

        if total and not line_id:
            columns = ['', '', '', '', '', '', total, '']
            lines.append({
                'id': 'total',
                'name': _('Total'),
                #'colspan': 7,
                'level': 0,
                'class': 'total',
                'columns': [{'name': v} for v in columns]
                })
        
        return lines
                
    def _get_report_name(self):
        return _('Sale Report/partner')
        
    