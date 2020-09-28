# -*- coding: utf-8 -*-

from odoo import fields, models, _


class AccountPartnerLedger(models.TransientModel):
    _inherit = "account.common.partner.report"
    _name = "account.report.partner.ledger"
    _description = "Account Partner Ledger"
    
    ACC_TYPES = [('receivable', 'Customer'), 
                 ('payable', 'Vendor'),
                 ('all', 'All')
                ]
    

    amount_currency = fields.Boolean("With Currency",
                                     help="It adds the currency column on report if the "
                                          "currency differs from the company currency.")
    reconciled = fields.Boolean('Reconciled Entries')
    partner_ids = fields.Many2many('res.partner', 'partner_custom_ledger_rel', string="Partner")
    account_type = fields.Selection(ACC_TYPES, string="Account Type", default='all')
    

    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency, 'partner': self.partner_ids})
        return self.env.ref('accounting_pdf_reports.action_report_partnerledger').report_action(self, data=data)
