# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError

class CustomPartnerLedger(models.AbstractModel):
    _name = 'report.hta_partner_ledger.custom_partner_ledger_template'
    _description = "Custom partner ledger"
    
    
    
    
    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('hta_partner_ledger.custom_partner_ledger_template')
    
    