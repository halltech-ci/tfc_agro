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
    
    
    def _get_lines(self, data):
        company_id = data['form']['company_id']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        partners = data['form']['partners']
        lines = []
        partners_obj = self.env['res.partner'].search([])
        #start_from += ' 00:00:00'
        #end_to += ' 23:59:59'
        company_obj = self.env['res.company']
        domain = [('payment_date', '>=', date_from), ('payment_date', '<=', date_to)]
        dom = [('date', '>=', date_from), ('date', '<=', date_to)]
        if len(partners) > 0:
            partner_obj = self.env['res.partner'].browse(partners)
        partners = sorted(partners_obj, key=lambda x: (x.ref or '', x.name or ''))
        check_id = company_obj.browse(company_id).check_on_hand_journal#check_deposit_transfer_account_id
        deposit_domain = [('deposit_date', '>=', date_from), ('deposit_date', '<=', date_to)]
        move_domain = [('account_id', '=', check_id.id)] + dom
        check_domain = [('journal_id.default_credit_account_id', '=', check_id.id)] + domain
        deposit_obj = self.env['account.check.deposit'].search(deposit_domain)
        check_obj = self.env['account.payment'].search(check_domain)
        check_move = self.env["account.move.line"].search(move_domain)
        for partner in partners_obj:
            partner_domain = [('journal_id.default_credit_account_id', '=', check_id.id)]
            check = check_obj.filtered(lambda l:l.partner_id == partner)
            deposit = deposit_obj.filtered(lambda d:d.move_id.partner_id == partner)
            aml = {
                'partner': partner,
                'deposit': deposit,
                'check': check,
                'check_move': check_move
            }
            lines.append(aml)
        return lines
    
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
           'get_lines': self._get_lines
        }
        return res
        

    