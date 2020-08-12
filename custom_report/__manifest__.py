# -*- coding: utf-8 -*-
{
    'name': "custom_report",

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
                'account_accountant',
                'account',
                'sale',
                'board',
                'stock',
               ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        #'views/account_payment_views.xml',
        #'views/res_partner_views.xml',
        'wizards/create_custom_report.xml',
        'reports/custom_report.xml',
        'reports/custom_report_template.xml',
        'reports/sale_custom_report.xml',
        #'reports/stock_custom_report.xml',
        'views/dashboard.xml',
        'views/res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}