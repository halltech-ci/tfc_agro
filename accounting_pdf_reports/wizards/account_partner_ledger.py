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
    
    """
    @api.onchange('account_type')
    @api.depends('account_type')
    def onchange_domain_on_days(self):
        res = {}
        ids = []
        domain = []
        partner_model = self.env['res.partner']
        acc_type = self.account_type
        if acc_type == 'customer':
            domain = [('customer', '=', True)]
        elif acc_type == 'supplier':
            domain = [('supplier', '=', True)]
        partners = partner_model.search(domain)
        for partner in partners:
            ids.append(partner.id)
        res['domain'] = {
            'id': [('id', 'in', ids)],
            }
        return res
    """
    
    """
    @api.onchange('account_type')
    def onchange_account_type(self):
    """    
    
    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency, 'partner': self.partner_ids,
                            'account_type': self.account_type})
        return self.env.ref('accounting_pdf_reports.action_report_partnerledger').report_action(self, data=data)
