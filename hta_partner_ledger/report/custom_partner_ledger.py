# -*- coding: utf-8 -*-
import pytz
import time
from operator import itemgetter
from itertools import groupby
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date, timedelta
import re


class CustomPartnerLedger(models.AbstractModel):
    _name = 'report.hta_partner_ledger.custom_partner_ledger_template'
    _description = "Custom partner ledger"
        
    def convert_withtimezone(self, userdate):
        user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATETIME_FORMAT)
        tz_name = self.env.context.get('tz') or self.env.user.tz
        if tz_name:
            utc = pytz.timezone('UTC')
            context_tz = pytz.timezone(tz_name)
            user_datetime = user_date
            local_timestamp = context_tz.localize(user_datetime, is_dst=False)
            user_datetime = local_timestamp.astimezone(utc)
            return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
    def _get_partner_move(self, partners):
        liste = []
        quer = """
            SELECT aml.id AS line_id, aml.product_id, aml.product_uom_id, aml.quantity, aml.account_id
            FROM account_move_line aml
            INNER JOIN account_move am  ON am.id = aml.move_id 
            INNER JOIN product_product pp ON pp.id = aml.product_id
            WHERE am.partner_id IS NOT NULL AND pp.id = aml.product_id
        """
        for partner in partners:
            partner_name = partner.name
            moves = self.env['account.move'].search([('partner_id', '=', partner.id)])
            dic = [partner, moves]
            liste.append(dic)
        return liste #Example [(res.partner(568,), account.move(92, 91, 42, 22))],
    
    def _get_partner_move_line(self, partners):
        moves = self._get_partner_move(partners)
        res = {}
        for move in moves:
            partner_id = move[0].id
            move_id = [a.id for a in move[1]]# all move_id for this partner
            dic = {partner_id : move_id}
            res.update(dic)#{'DIALLO AMADOU': ['INV/2020/0144', 'INV/2020/0143', 'INV/2020/0062', 'INV/2020/0031', 'INV/2020/0011'],
        return res
    '''
    def _get_account_move_detail(self, move_id):
        lines = self.env['account.move'].search([('id', '=', move_id)]).line_ids
        for line in lines:
    '''     
            
        
    def _get_lines(self, record, partners=None):
        partner_ids = []
        start_date = str(date.today().replace(month=1, day=1)) if not record.start_date else str(record.start_date)
        end_date = str(date.today()) if not record.end_date else str(record.end_date)  
        date_from = self.convert_withtimezone(start_date)
        date_to = self.convert_withtimezone(end_date)
        domain = [('date', '>=', date_from), ('date', '<=', date_to)]
        if partners:
            for partner in partners_ids:
                partner_ids.append(partner.id)
            #domain.append(('partner_id', 'in', partner_ids))
        elif records.partner_ids:
            for partner in records.partner_ids:
                partner_ids.append(partner.id)
            #domain.append(('partner_id', 'in', partner_ids))
                                    
    @api.model
    def _get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name('hta_partner_ledger.custom_partner_ledger_template')
        record_id = data['form']['id'] if data and data.get('form', False) and data.get('form').get('id', False) else docids[0]
        records = self.env['custom.partner.ledger'].browse(record_id)
        docids = records.ids
        res = {
           'doc_model': report.model,
           'doc_ids': docids,
           'docs': records,
           'data': data,
           'lang': "fr_FR",
           'get_partner_move': self._get_partner_move
        }
        return res
    
    quer = """
            SELECT p.id, am.id AS move_id
            FROM account_move_line aml
            INNER JOIN account_move am  ON am.id = aml.move_id 
            INNER JOIN product_product pp ON pp.id = aml.product_id
            INNER JOIN res_partner p ON p.id = am.partner_id
            WHERE am.partner_id IS NOT NULL
            GROUP BY am.id, p.id
        """#Example {'id': 663, 'move_id': 54}
        
        
