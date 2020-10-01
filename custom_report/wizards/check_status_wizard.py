from odoo import models, fields, api, _

class CheckStatusWizard(models.TransientModel):
    _name="check.status.wizard"
    _description="Wizard form to to filter sale report"
    
    date_from = fields.Date(string="From Date", default=fields.Date.today())
    date_to = fields.Date(string="To Date", default=fields.Date.today())
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    partner_ids = fields.Many2many('res.partner', 'partner_check_status_rel', string="Partner")
    
    def check_date_range(self):
        if self.date_to < self.date_from:
            raise ValidationError(_('Enter proper date range'))
            
    #Get data from the form
    @api.multi
    def _print_report(self, data):
        data = self.pre_print_report(data)
        partners = [p.id for p in self.partner_ids]
        data['form'].update({'company':self.company_id.id, "date_from": self.date_from, "date_to": self.date_to, 'partner': partners})
        return self.env.ref('custom_report.action_report_check_status').report_action(self, data=data)
    
    