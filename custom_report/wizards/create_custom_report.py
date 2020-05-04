# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
#from datetime import datetime, date
#from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, date_utils

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


class CreateCustomReport(models.TransientModel):
    _name="create.custom.report"
    _description="Wizard form to create custom report"
    
    date_from = fields.Date(string="From Date", default=fields.Date.today())
    date_to = fields.Date(string="Today", required=True, default=fields.Date.today())
    
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
    
    

'''
class CreateCustomReport(models.TransientModel):
    _name="create.custom.report"
    _description="Wizard form to create custom report"

    compute_at_date = fields.Selection([
        (0, 'Current Inventory'),
        (1, 'At a Specific Date')
    ], string="Compute", help="Choose to analyze the current inventory or from a specific date in the past.")
    date = fields.Datetime('Inventory at Date', help="Choose a date to get the inventory at that date", default=fields.Datetime.now)

    def open_table(self):
        self.ensure_one()

        if self.compute_at_date:
            tree_view_id = self.env.ref('stock.view_stock_product_tree').id
            form_view_id = self.env.ref('stock.product_form_view_procurement_button').id
            # We pass `to_date` in the context so that `qty_available` will be computed across
            # moves until date.
            action = {
                'type': 'ir.actions.act_window',
                'views': [(tree_view_id, 'tree'), (form_view_id, 'form')],
                'view_mode': 'tree,form',
                'name': _('Products'),
                'res_model': 'product.product',
                'domain': "[('type', '=', 'product')]",
                'context': dict(self.env.context, to_date=self.date),
            }
            return action
        else:
            self.env['stock.quant']._merge_quants()
            self.env['stock.quant']._unlink_zero_quants()
            return self.env.ref('stock.quantsact').read()[0]
'''