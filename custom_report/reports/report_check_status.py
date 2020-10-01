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
    
    
    def _get_lines(self, docids, data=None):
        company_id = data['form']['company']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        partners = data['form']['partner']
        lines = []
        #start_from += ' 00:00:00'
        #end_to += ' 23:59:59'
        domain = [('date', '>=', date_from), ('date', '<=', date_to)]
        if len(partners) > 0:
            partner_obj = self.env['res.partner'].browse(partners)
        else:
            partners_obj = self.env['res.partner'].search([])
        partners = sorted(partners_obj, key=lambda x: (x.ref or '', x.name or ''))
        #pdc_account_id = company.pdc_check_account.id
        check_deposit_account_id = company.check_deposit_transfer_acoount_id.id
        deposit_domain = [('account_id', '=', check_deposit_account_id)] + domain
        check_receive_account_id = company.check_on_hand_journal.id
        check_rec_domain = [('account_id', '=', check_receive_account_id.id)] + domain
        req_orm = self.env['account.move.line']
        check_deposit_obj = req_orm.search(deposit_domain)
        check_on_hand_obj = req.orm.search(check_rec_domain)
        for partner in partners_obj:
            deposit = check_deposit_obj.filtered(lambda l:l.partner_id == partner_id)
            receive = check_on_hand_obj.filtered(lambda l:l.partner_id == partner_id)
            aml = {
                'partner': partner,
                'deposit': deposit,
                'receive': receive
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
           'get_lines': self.get_lines
        }
        return res
        

    