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

class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"
    
    transaction_type = fields.Selection([('pdc', 'Post Dated Check'), ('security', 'Security'), ('deposited', 'To Be Deposited')], string="Check Type", default='pdc')


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    transaction_type = fields.Selection([('pdc', 'Post Dated Check'), ('security', 'Security'), ('deposited', 'To Be Deposited')], string="Check Type", default='pdc')
    