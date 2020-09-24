# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError

class CustomPartnerLedger(models.AbstractModel):
    _name = 'report.hta_partner_ledger.custom_partner_ledger_template'
    _description = "Custom partner ledger"
    
    