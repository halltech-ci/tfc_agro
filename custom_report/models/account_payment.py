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

class AccountPayment(models.Model):
    _inherit = "account.payment"

    bank_reference = fields.Char(copy=False)
    cheque_reference = fields.Char(copy=False)
    effective_date = fields.Date('Effective Date', help='Effective dateC', copy=False, default=False)
    payment_note = fields.Selection([('pdc', 'Post Dated Check'), ('security', 'Security')], default='')
    
class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.register.payments"

    bank_reference = fields.Char(copy=False)
    cheque_reference = fields.Char(copy=False)
    effective_date = fields.Date('Effective Date', help='Effective date', copy=False, default=False)
    payment_note = fields.Selection([('pdc', 'Post Dated Check'), ('security', 'Security'), ('deposited', 'To Be Deposited')], default='')