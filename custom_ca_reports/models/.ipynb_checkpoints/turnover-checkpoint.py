# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, models, _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError
from odoo.addons.web.controllers.main import clean_action


class ReportTurnoverCountry(models.AbstractModel):
    _name = "account.report.turnover.country"
    _description = "Turnover by country/partner"
    _inherit = 'account.report'

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_all_entries = False

    def get_columns_name(self, options):
        return [{'name': _('Customer')}, {'name': _('Turnover'), 'class': 'number'}]

    @api.model
    def get_lines(self, options, line_id=None):
        lines = []
        #tables, where_clause, where_params = self.env['account.move.line'].with_context(strict_range=True)._query_get()
        user_type_id = self.env['account.account.type'].search([('type', '=', 'receivable')])
        if where_clause:
            where_clause = 'AND ' + where_clause
        # When unfolding, only fetch sum for the country we are unfolding and
        # fetch all partners for that country
        
        sql_query = """
            SELECT sum(\"aml\".balance) AS balance, p.name, p.id FROM account_move_line aml, res_partner p
                WHERE aml.partner_id = p.id AND p.customer = True
                GROUP BY p.name, p.id
        """
        
        params = [user_type_id.id] + where_params
        self.env.cr.execute(sql_query)
        results = self.env.cr.dictfetchall()

        total = 0
        for line in results:
            total += line.get('balance')
            lines.append({
                    'id': line.get('id'),
                    'name': line.get('name'),
                    'level': 2,
                    'unfoldable': False,
                    'columns': [{'name': line.get('balance')}],
                })
        # Adding partners lines
        # Don't display level 0 total line in case we are unfolding
        return lines

    def get_report_name(self):
        return _('Turnover by country/partner')
