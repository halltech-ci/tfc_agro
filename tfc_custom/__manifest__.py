# -*- coding: utf-8 -*-
{
    'name': "tfc_custom",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
               'product',
               'purchase',
               'sale_management',
               'sale_stock',
                'account_accountant',
               ],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        #'views/product_template_views.xml',
        'views/sale_order_views.xml',
        'reports/sale_order_report.xml',
        'reports/purchase_order_report.xml',
        'reports/account_invoice_report.xml',
        'data/sale_order_ir_sequence.xml',
        'data/stock_picking_ir_sequence.xml',
        'data/purchase_ir_sequence.xml',
        'views/stock_picking_views.xml',
        'reports/stock_picking_report.xml',
        'views/account_invoice_views.xml',
        'views/purchase_order_views.xml',
        'views/res_partner_views.xml',
        'views/stock_production_views.xml'
        #'wizards/create_custom_report.xml',
        #'reports/custom_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}