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
    
    date_from = fields.Datetime(string="From Date")
    date_to = fields.Datetime(string="To Date")
    
    @api.multi
    def print_report(self):
        #I get data enter in form
        data = {
            'model': self._name,
            'ids' : self.ids,
            'form' :{
                'from_date': self.date_from,
                'to_date' : self.date_to
            }
            #'form' : self.read()[0]
        }
        #custom_report is the report template name
        return self.env.ref('tfc_custom.custom_report').with_context(landscape=True).report_action(self, data=data)