# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.common.partner.report"
    _name = "account.report.partner.ledger"
    _description = "Account Partner Ledger"
    
    ACC_TYPES = [('customer', 'Customer'), 
                 ('supplier', 'Vendor'),
                 ('all', 'All')
                ]
    

    amount_currency = fields.Boolean("With Currency",
                                     help="It adds the currency column on report if the "
                                          "currency differs from the company currency.")
    reconciled = fields.Boolean('Reconciled Entries')
    partner_ids = fields.Many2many('res.partner', 'partner_custom_ledger_rels', string="Partner")
    account_type = fields.Selection(ACC_TYPES, string="Account Type", default='customer')
    
    def _print_report(self, data):
        data = self.pre_print_report(data)
        partners = [p.id for p in self.partner_ids]
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency, 'partner': partners,
                            'account_type': self.account_type})
        return self.env.ref('custom_report.action_custom_partner_ledger').report_action(self, data=data)
