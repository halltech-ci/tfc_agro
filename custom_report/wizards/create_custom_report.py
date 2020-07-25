# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from io import BytesIO
import xlwt
import base64
from datetime import datetime, date


class CreateCustomReport(models.TransientModel):
    _name="create.custom.report"
    _description="Wizard form to create custom report"
    
    date_from = fields.Date(string="From Date", default=fields.Date.today())
    date_to = fields.Date(string="Today", required=True, default=fields.Date.today())
    warehouse_ids = fields.Many2many('stock.warehouse', 'warehouse_custom_report_rel', string="Warehouse", required=True)
    location_id = fields.Many2one('stock.location', string="Location")
    filter_by = fields.Selection([('product', 'Product'), ('category', 'Category')], string="Filter By")
    group_by_categ = fields.Boolean(string="Category Group By")
    with_zero = fields.Boolean(string="With Zero Values")
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    name = fields.Char(string='File Name', readonly=True)
    data = fields.Binary(string='File', readonly=True)
    product_ids = fields.Many2many('product.product', 'product_custom_report_rel', string="Products")
    category_ids = fields.Many2many('product.category', 'product_categ_custom_report_rel', string="Categories")
    is_today_movement = fields.Boolean(string="Today Movement")

    
    @api.multi
    def get_report(self):
        #I get data enter in form
        data = {
            'model': self._name,
            'ids' : self.ids,
            #data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
            'form' :self.read(['date_from', 'date_to'])[0]
            #'form' : self.read()[0]
        }
        #action_custom_report is the report template name
        return self.env.ref('custom_report.action_custom_report').with_context(landscape=True).report_action(self, data=data)
    
    
