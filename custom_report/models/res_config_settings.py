# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class custom_report(models.Model):
#     _name = 'custom_report.custom_report'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    
    pdc_check_account = fields.Many2one(related="company_id.pdc_check_account", string="PDC Account")
    check_on_hand_journal = fields.Many2one(related="company_id.check_on_hand_journal", string="Check On Hand account")
    check_on_bank_journal = fields.Many2one(related="company_id.check_on_bank_journal", string="Check on Bank account")