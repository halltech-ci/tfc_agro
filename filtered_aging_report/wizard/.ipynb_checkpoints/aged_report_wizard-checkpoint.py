# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
import base64
import tempfile
import os, io

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class account_aged_partner_wizard(models.TransientModel):
    _name = "account.aged.partner.wizard"
    _description = "Account Aged Partner Wizard"
    
    date = fields.Date("Date", required=True)
    type = fields.Selection([('balances','Balances'),('Detailed','Detailed')],default="balances", required=True, string='Type')
    aging_type = fields.Selection([('receivable','Receivable'),('payable','Payable')],default="receivable", required=True, string='Aging Type')
    group_by = fields.Selection([('state','State')], 'Group by')
    ignore_limit = fields.Float('Ignore Limit')
    note = fields.Text('Note')
    datas = fields.Binary()
    datas_fname = fields.Char()
    
    
    def get_lines(self):
        options = self.export_data()
        aap = self.env['account.aged.partner']
        context = self._context
        if self.aging_type == 'receivable':
            report_manager = self.env['account.aged.receivable']._get_report_manager(options)
            report_manager.summary = self.note
        else:
            report_manager = self.env['account.aged.payable']._get_report_manager(options)
            report_manager.summary = self.note
        
        partners = self._context.get("active_ids",[])
        if context.get("select_all",False):
            partner_ids = self.env["res.partner"].search(context.get("active_domain"))
        else :
            partner_ids = self.env['res.partner'].browse(partners)
        
        
        account_types = [self.aging_type]
        res, total, amls = self.env['report.account.report_agedpartnerbalance'].with_context(include_nullified_amount=True,partner_ids=partner_ids)._get_partner_move_lines(account_types, self.date,'posted', 30)
        ignore_limit = self.ignore_limit
          
          
        if self.aging_type ==  "receivable":
            res = [r for r in res if r["total"]>=ignore_limit]
        elif self.aging_type == "payable" :
            res = [r for r in res if r["total"]>=ignore_limit]
         
         
         
          
        ids = [d["partner_id"] for d in res] 
        partners = self.env["res.partner"].browse(ids) 
        
        
        aged_balance = True if self.aging_type == 'payable' else False
        
        
        options["partner_ids"] = ids
        
        if not partners:
            return []
        
        lines = aap.with_context(date_to=self.date,account_type=self.aging_type,partner_ids=partners,aged_balance=aged_balance,ignore_limit=self.ignore_limit)._get_lines(options)
        
        
        
        if self.group_by == 'state':
            states = {'Non-State': {'cols':[]}, 'Total':{'cols':[]}}
            
            for line in lines:
                id  = line.get('id') if line.get('level') == 2 else line.get('parent_id')
                if id != 0:
                    d = id.split('_')
                    partner = self.env['res.partner'].browse(int(d[1]))
                    if partner.state_id.name not in states:
                        if partner.state_id:
                            states[partner.state_id.name] = {'cols':[line]}
                        else:
                            states['Non-State']['cols'].append(line)
                    else:
                        states[partner.state_id.name]['cols'].append(line)
                elif id == 0:
                    states['Total']['cols'].append(line)
            return states
        return lines
        
    
    def excel_report(self, id):
        action =  {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_xls_document_aging/?model=account.aged.partner.wizard&id=%s' % (id),
            'target': 'new',
        }
        return action
        
    
    def export_excel(self):
        lines = {}
        lines['lines'] = self.get_lines()
        lines['rep_data'] = {}
        lines['rep_data']['date'] = self.date
        lines['rep_data']['date_print'] = fields.Date.today()
        parnters_name = ''
        partners = self._context.get("active_ids",[])
        partner_ids = self.env['res.partner'].browse(partners)
        for p in partner_ids:
            parnters_name += p.name+', '
        parnters_name = parnters_name[:-2]
        report_name = 'Aged Payable' if self.aging_type == 'payable' else 'Aged Receivable'
        
        
        temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx")
        workbook = xlsxwriter.Workbook(temp_file.name)
        sheet = workbook.add_worksheet('Aging-Report')
        
        haeder = workbook.add_format({'bold': 1,
                                      'border': 1,
                                      'align': 'center',
                                      'valign': 'vcenter',
                                      'font_size':20,
                                      'text_wrap': 1})
        line_left = workbook.add_format({'align': 'left',
                                    'font_size':10,})
        line_left1 = workbook.add_format({'align': 'left',
                                    'font_size':10,'bold': 1,})
        line_right = workbook.add_format({'align': 'right',
                                    'font_size':10,})
        line_right1 = workbook.add_format({'align': 'right',
                                    'font_size':10,'bold': 1,})
        
        sheet.set_column('A:A', 25)
        sheet.set_column('B:B', 19)
        sheet.set_column('C:C', 14)
        sheet.set_column('D:D', 14)
        sheet.set_column('E:E', 14)
        sheet.set_column('F:F', 14)
        sheet.set_column('G:G', 14)
        sheet.set_column('H:H', 14)
        
        report_name = 'Aged Payable' if self.aging_type == 'payable' else 'Aged Receivable'
        sheet.merge_range(3, 3, 5, 6, report_name, haeder)
        
        p_ids = partner_ids.mapped('user_id').ids
        sp = list(set(p_ids))
        
        sheet.write('A7', 'Date', line_left1)
        sheet.write('A8', str(self.date), line_left)
        
        sheet.write('C7', 'Print Date', line_left1)
        sheet.write('C8', str(fields.Date.today()), line_left)
        if len(sp) == 1:
            sheet.write('E7', 'Salesperson', line_left1)
            sheet.write('E8', self.env['res.users'].browse(sp[0]).name , line_left)
        
        sheet.write('A11', '', line_left1)
        sheet.write('B11', 'Not due on: '+str(self.date), line_left1)
        sheet.write('C11', '1 - 30', line_right1)
        sheet.write('D11', '31 - 60', line_right1)
        sheet.write('E11', '61 - 90', line_right1)
        sheet.write('F11', '91 - 120', line_right1)
        sheet.write('G11', 'Older', line_right1)
        sheet.write('H11', 'Total', line_right1)
        
        x=12
        datas = lines['lines']
        total = {}
        if self.group_by == 'state':
            for d in datas:
                if d != 'Total':
                    sheet.write('A%s'%x, d, line_left1)
                    x+=1
                    cols = datas[d]['cols']
                    for col in cols:
                        if col['name'] != 'Total':
                            if col['level'] == 2:
                                sheet.write('A%s'%x, "     "+col['name']+"     ", line_left1)
                            elif col['level'] == 4:
                                sheet.write('A%s'%x, "          "+col['name']+"          ", line_left1)
                            sheet.write('B%s'%x, col['columns'][3]['name'], line_right)
                            sheet.write('C%s'%x, col['columns'][4]['name'], line_right)
                            sheet.write('D%s'%x, col['columns'][5]['name'], line_right)
                            sheet.write('E%s'%x, col['columns'][6]['name'], line_right)
                            sheet.write('F%s'%x, col['columns'][7]['name'], line_right)
                            sheet.write('G%s'%x, col['columns'][8]['name'], line_right)
                            sheet.write('H%s'%x, col['columns'][9]['name'], line_right)
                            x+=1
                elif d == 'Total':
                    total = datas[d]['cols'][0] if datas[d]['cols'] else False 
            if total:
               sheet.write('A%s'%x, total['name'], line_left1)
               sheet.write('B%s'%x, total['columns'][3]['name'], line_right)
               sheet.write('C%s'%x, total['columns'][4]['name'], line_right)
               sheet.write('D%s'%x, total['columns'][5]['name'], line_right)
               sheet.write('E%s'%x, total['columns'][6]['name'], line_right)
               sheet.write('F%s'%x, total['columns'][7]['name'], line_right)
               sheet.write('G%s'%x, total['columns'][8]['name'], line_right)
               sheet.write('H%s'%x, total['columns'][9]['name'], line_right)
               x+=1
        elif self.group_by != 'state':
            for d in datas:
                if d['name'] != 'Total':
                    if d['level'] == 2:
                        sheet.write('A%s'%x, "     "+d['name']+"     ", line_left1)
                    elif d['level'] == 4:
                        sheet.write('A%s'%x, "          "+d['name']+"          ", line_left1)
                    sheet.write('B%s'%x, d['columns'][3]['name'], line_right)
                    sheet.write('C%s'%x, d['columns'][4]['name'], line_right)
                    sheet.write('D%s'%x, d['columns'][5]['name'], line_right)
                    sheet.write('E%s'%x, d['columns'][6]['name'], line_right)
                    sheet.write('F%s'%x, d['columns'][7]['name'], line_right)
                    sheet.write('G%s'%x, d['columns'][8]['name'], line_right)
                    sheet.write('H%s'%x, d['columns'][9]['name'], line_right)
                    x+=1
                elif d['name'] == 'Total':
                    total = d
            if total:
               sheet.write('A%s'%x, total['name'], line_left1)
               sheet.write('B%s'%x, total['columns'][3]['name'], line_right)
               sheet.write('C%s'%x, total['columns'][4]['name'], line_right)
               sheet.write('D%s'%x, total['columns'][5]['name'], line_right)
               sheet.write('E%s'%x, total['columns'][6]['name'], line_right)
               sheet.write('F%s'%x, total['columns'][7]['name'], line_right)
               sheet.write('G%s'%x, total['columns'][8]['name'], line_right)
               sheet.write('H%s'%x, total['columns'][9]['name'], line_right)
               x+=1
        
        workbook.close()
        data = open(temp_file.name, 'rb').read()
        self.datas = base64.b64encode(data)
        self.datas_fname = "Aging-Report.xlsx"
        temp_file.close()
        filename = temp_file.name
        return self.excel_report(self.id)
    
    
    def export_pdf(self):
        lines = {}
        lines['lines'] = self.get_lines()
        lines['rep_data'] = {}
        lines['rep_data']['date'] = self.date
        lines['rep_data']['date_print'] = fields.Date.today()
        parnters_name = ''
        partners = self._context.get("active_ids",[])
        partner_ids = self.env['res.partner'].browse(partners)
        for p in partner_ids:
            parnters_name += p.name+', '
        parnters_name = parnters_name[:-2]
        report_name = 'Aged Payable' if self.aging_type == 'payable' else 'Aged Receivable'
        
        lines['rep_data']['parts'] = parnters_name
        lines['rep_data']['rep_name'] = report_name
        lines['rep_data']['note'] = self.note if self.note else False
        lines['rep_data']['state'] = True if self.group_by == 'state' else False
        p_ids = partner_ids.mapped('user_id').ids
        sp = list(set(p_ids))
        lines['rep_data']['salesperson'] = self.env['res.users'].browse(sp[0]).name if len(sp) == 1 else False
        return self.env.ref('filtered_aging_report.action_report_aged').with_context(landscape=True).report_action(self, data=lines)
    
    
    def export_data(self):
        aap = self.env['account.aged.partner'] 
        context = self._context
        
        options = aap._build_options()
        unfolded_lines = []
        partners = self._context.get("active_ids",[])
        
        partner_ids = self.env['res.partner'].browse(partners)
        
        if self.aging_type == "receivable":
            partner_ids = partner_ids.filtered(lambda x: (x.credit >= (self.ignore_limit)) or (x.credit < -1*self.ignore_limit)).ids
        elif self.aging_type == "payable":
            partner_ids = partner_ids.filtered(lambda x: (x.debit >= (self.ignore_limit)) or (x.debit < -1*self.ignore_limit)).ids
        else:
            partner_ids = partner_ids.filtered(lambda x: (x.balance >= (self.ignore_limit)) or (x.balance < -1*self.ignore_limit)).ids
            
        
        options['partner_ids'] = partner_ids
        if self.type =='Detailed':
            for id in partner_ids:
                unfolded_lines.append("partner_%s"%id)
        options['unfolded_lines'] = unfolded_lines
            
        if options.get('partner'):
            options['selected_partner_ids'] = []
            options['selected_partner_categories'] = []
        return options
        
