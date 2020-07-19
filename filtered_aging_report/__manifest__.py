# -*- coding: utf-8 -*-
{
    'name': "SW - Filtered Aging Report",

    'summary': """Print your aging reports with custom filters.
			""",
    'description': """Generate & Print your Odoo Aging Reports for certain contacts using custom filters.
    """,
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Accounting',
    'version': '12.0.1.0',
    'depends': ['base','account_reports'],
    'license':  "Other proprietary",
    'installable': True,
    'auto_install': False,
    'data': [
        'report/layout.xml',
        'wizard/aged_report_wizard_view.xml',
        'report/report_partnerledger.xml',
        'data/account_financial_report_data.xml',
    ],
    'images':  ["static/description/image.png"],
}
