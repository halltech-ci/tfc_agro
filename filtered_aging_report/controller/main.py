# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request,content_disposition
import base64

class Controller(http.Controller):
    
    @http.route('/web/binary/download_xls_document_aging', type='http', auth="user")
    def download_document(self,model ,id, **kwargs):
        summ = request.env[model].browse(int(id))
        file = base64.b64decode(summ.datas)
        file_name = summ.datas_fname
        return request.make_response(file,
                                      [('Content-Type', 'text/plain'),
                                         ('Content-Disposition' ,content_disposition(file_name ))])