# -*- coding: utf-8 -*-

import time
from odoo import api, models, fields, _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError
from odoo.addons.web.controllers.main import clean_action

from datetime import datetime, date
from odoo.tools.misc import format_date

class SaleCustomReports(models.AbstractModel):
    _name = "account.report.customer.reports"
    _inherit = "account.report"
    _description = "customer report"
    
    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}
    filter_partner = True
    
    def _get_columns_name(self, options):
        columns = [
            {'name': _('Customer')},
            {'name': _('Credit Limit'), 'class': 'number'},
            {'name': _('Check On Hand'), 'class': 'number'},
            {'name': _('Check On Bank'), 'class': 'number'},
        ]

        if self.user_has_groups('base.group_multi_currency'):
            columns.append({'name': _('Amount Currency'), 'class': 'number'})
        return columns
    
    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []
        domain = [('partner_type', '=', 'customer'), ('move_reconciled', '!=', True)]
        date_from = options['date'].get('date_from')
        date_to = options['date'].get('date_to')
        date_from_datetime = fields.Datetime.from_string(date_from)
        date_to_datetime = fields.Datetime.from_string(date_to)
        domain=[('payment_date', '>=', date_from), ('date_order', '<=', date_to)] + domain
        #context = self.env.context
        query = """
            SELECT sum(pay.amount) AS amount, pay.journal_id, p.id as partner_id, p.credit_limit
            FROM account_payment pay, res_partner p
            WHERE pay.partner_id = p.id
            GROUP BY pay.journal_id, p.id    
        """
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        #self.env['account.payment'].with_context(strict_range=True).search(domain)
        for line in results:
            
            partner_name = self.env['res.partner'].browse(line.get('partner_id')[0]).name
            columns = [partner_name, line.get('credit_limit'), line.get('journal_id'), line.get('journal_id')]
            lines.append({
                'id': line.get('partner_id'),
                'name': partner_name,
                'level': 2,
                'unfoldable': True,
                'unfolded': line_id == line.get('partner_id') and True or False,
                'columns':[{'name': v} for v in columns],
            })
        return lines
    
    def _get_report_name(self):
        return _('Customer State Report')
        
        
        