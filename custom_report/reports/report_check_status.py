# -*- coding: utf-8 -*-

import pytz
import time
from operator import itemgetter
from itertools import groupby
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date, timedelta
import re

class ReportCheckStatus(models.AbstractModel):
    _name="report.custom_report.report_check_template"#Respect naming format report.module_name.report_template_name
    _description="Check status report for TFC AGRO"
      
    def _get_check_status(self, data, partner):
        date_from = fields.Date.to_date(data['form']['date_from'])
        date_to = fields.Date.to_date(data['form']['date_to'])
        company_id = data['form']['company_id']
        company = self.env['res.company'].browse(company_id)
        check_account = company.check_on_hand_journal
        domain = [('date', '>=', date_from), ('date', '<=', date_to)]
        deposit_domain = [('check_deposit_id', '!=', False)] + domain
        payment_domain = [('payment_date', '>=', date_from), ('payment_date', '<=', date_to), ('journal_id.default_debit_account_id', '=', check_account.id), ('partner_id', '=', partner.id)]
        check_domain = [('check_deposit_id', '=', False), ('account_id', '=', check_account.id)] + domain
        payments = self.env['account.payment'].search(payment_domain)
        res = {
            'payments': payments
        }
        return res
    
    def _sum_payment_line(self, line_ids):
        sum = 0.0
        for line in line_ids:
            sum += line.amount 
        req = self.env['account.payment'].search([('id', '=', payment.id)])
        deposit = self.env['account.check.deposit']
    
    def _get_partners(self, data):
        partner_obj = self.env['res.partner']
        partners = partner_obj.search([('customer', '=', True)])
        partner_ids = data['form']['partners']
        if len(partner_ids) > 0:
            partners = partner_obj.browse(partner_ids)
        return partners
    
    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
            
        report = self.env['ir.actions.report']._get_report_from_name('custom_report.report_check_template')
        record_id = data['form']['id'] if data and data.get('form', False) and data.get('form').get('id', False) else docids[0]
        records = self.env['check.status.wizard'].browse(record_id)
        docids = records.ids
        res = {
           'doc_model': report.model,
           'doc_ids': docids,
           'docs': records,
           'data': data,
           'lang': "fr_FR",
           'payments': self._get_check_status,
           'partners': self._get_partners
        }
        return res
        

    