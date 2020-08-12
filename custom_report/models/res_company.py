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


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    pdc_check_account = fields.Many2one("account.account", string="PDC Account")
    check_on_hand_journal = fields.Many2one("account.account", string="Check On Hand Account")
    check_on_bank_journal = fields.Many2one("account.account", string="Check on Bank Account")