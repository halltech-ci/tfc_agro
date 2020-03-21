# -*- coding: utf-8 -*-

from odoo import models, fields, api
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
    
    date_from = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    
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
        return self.env.ref('tfc_custom.action_custom_report').with_context(landscape=True).report_action(self, data=data)