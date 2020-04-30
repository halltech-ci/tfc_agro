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
    
    '''
    @api.one
    def _get_bank_ids(self):
        if self.partner_bank_account_id :
            self.customer_bank = self.env['res.partner.bank'].browse[self.partner_id.bank_ids].mapped('bank_name')
        else:
            self.customer_bank = False
    '''
    partner_id = fields.Many2one('res.partner', string='Partner')
    customer_bank = fields.Many2one('res.partner.bank', string="Partner Bank")
    cheque_number = fields.Char(string="Cheque Reference")