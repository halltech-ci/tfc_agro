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
    
    start_date = fields.Date(string="From Date", default=fields.Date.today())
    end_date = fields.Date(string="Today", required=True, default=fields.Date.today())
    warehouse_ids = fields.Many2many('stock.warehouse', 'warehouse_custom_report_rel', string="Warehouse", required=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id.id, required=True)
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
    #partner_ids = fields.Many2many('res_partner', 'partner_custom_report_rel', string="Partners")
    partner_type = fields.Selection([('customer', 'Customer'), ('suplier', 'Vendor')], string='Purchase/Sale')
    period_length = fields.Integer(string="Periods Length")
    period_wide = fields.Integer(string = "Period_wide", default=6)
    debtor_age_wise = fields.Boolean(string="Debtor Agewise", default=True)
    customer_age_wise = fields.Boolean(string="Customer Agewise", default=True)
    stock_age_wise = fields.Boolean(string="Stock Agewise", default=True)
    pdc_account = fields.Char(string="PDC Account", default='pdc')
    check_on_hand_account = fields.Char(string="Check on hand", default='51300000')
    check_on_bank = fields.Char(string="Check on Bank", default='51400000')
    
    @api.onchange('warehouse_ids')
    def onchange_warehouse_ids(self):
        if self.warehouse_ids:
            self.location_id = False

    @api.onchange('filter_by')
    def onchange_filter_by(self):
        self.product_ids = self.category_ids = False

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            self.warehouse_ids = self.location_id = False

    def check_date_range(self):
        if self.end_date < self.start_date:
            raise ValidationError(_('Enter proper date range'))
    
    def check_period_wide(self):
        if self.period_wide:
            if self.period_wide < self.period_length:
                raise ValidationError(_('Period Wide must be greater than period length'))
            
    @api.multi
    def generate_pdf_report(self):
        self.check_date_range()
        #self.check_period_range()
        datas = {'form':
            {
                'company_id': self.company_id.id,
                'warehouse_ids': [y.id for y in self.warehouse_ids],
                'location_id': self.location_id and self.location_id.id or False,
                'start_date': date.today() if self.is_today_movement else self.start_date,
                'end_date': date.today() if self.is_today_movement else self.end_date,
                'id': self.id,
                'product_ids': self.product_ids.ids,
                'product_categ_ids': self.category_ids.ids
            },
        }
        return self.env.ref('custom_report.action_custom_report').report_action(self, data=datas)
    
    @api.multi
    def generate_xls_report(self):
        self.check_date_range()
        pass

    
class stock_location(models.Model):
    _inherit = 'stock.location'

    @api.model
    def name_search(self, name, args, operator='ilike', limit=100):
        if self._context.get('company_id'):
            domain = [('company_id', '=', self._context.get('company_id')), ('usage', '=', 'internal')]
            if self._context.get('warehouse_ids') and self._context.get('warehouse_ids')[0][2]:
                warehouse_ids = self._context.get('warehouse_ids')[0][2]
                stock_ids = []
                for warehouse in self.env['stock.warehouse'].browse(warehouse_ids):
                    stock_ids.append(warehouse.view_location_id.id)
                domain.append(('location_id', 'child_of', stock_ids))
            args += domain
        return super(stock_location, self).name_search(name, args, operator, limit)

