# -*- coding: utf-8 -*-

from odoo import api, models
    
class AgedReport(models.AbstractModel):
    _name = 'report.filtered_aging_report.aged_report'
    _description = 'Report Filtered Aging Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'data':data,
        }