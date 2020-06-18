from odoo import models, fields, api, _

class SaleReportWizard(models.TransientModel):
    _name="sale.report.wizard"
    _description="Wizard form to to filter sale report"
    
    date_from = fields.Date(string="From Date", default=fields.Date.today())
    date_to = fields.Date(string="To Date", default=fields.Date.today())
    
    #Get data from the form
    @api.multi
    def get_sale_report(self):
        #I get data enter in form
        data = {
            'model': self._name,
            'ids' : self.ids,
            #data['form'] = self.read(['date_from', 'date_to', 'journal_ids', 'target_move', 'company_id'])[0]
            'form' :self.read(['date_from', 'date_to'])[0]
            #'form' : self.read()[0]
        }
        #action_custom_report is the report template name
        return self.env.ref('custom_report.action_sale_report_filter').with_context(landscape=True).report_action(self, data=data)