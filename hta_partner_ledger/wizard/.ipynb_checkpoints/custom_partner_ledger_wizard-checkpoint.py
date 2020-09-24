# -*- coding: utf-8 -*-

import time
from odoo import api, models, fields, _
from odoo.exceptions import UserError

class CustomPartnerLedger(models.TransientModel):
    _name="custom.partner.ledger"
    _description="Wizard for custom partner ledger"
    
    ACC_TYPES = [('receivable', 'Customer'), 
                 ('payable', 'Vendor'),
                 ('all', 'All')
                ]
    
    
    account_type = fields.Selection(ACC_TYPES, string="Account Type")
    partner_ids = fields.Many2many('res.partner', 'partner_custom_ledger_rel', string="Partner")
    start_date = fields.Date(string="From Date", default=fields.Date.today())
    end_date = fields.Date(string="To Date", required=True, default=fields.Date.today())
    
    def check_date_range(self):
        if self.end_date < self.start_date:
            raise ValidationError(_('Enter proper date range'))
    
    @api.multi
    def generate_pdf_report(self):
        self.check_date_range()
        #self.check_period_range()
        datas = {'form':
            {
                'account_type': self.account_type,
                'partner_ids': [y.id for y in self.partner_ids],
                'start_date': self.start_date,
                'end_date': self.end_date,
                'id': self.id,
            },
        }
        return self.env.ref('hta_partner_ledger.action_custom_partner_ledger').report_action(self, data=datas)
    
    