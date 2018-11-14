# -*- coding: utf-8 -*-
{
    'name': "Manufacturing data control (MDC)",

    'summary': """
        Introduces Manufacturing data control (MDC) process in Odoo""",

    'description': """
        Manufacturing data control (MDC)
    """,

    'author': "Solvos Consultoría Informática",
    'website': "http://www.solvos.es",

    'category': 'Manufacturing',
    'license': 'LGPL-3',
    'version': '0.1',

    'depends': ['base', 'product', 'hr', 'hr_contract', 'stock', 'report_xlsx'],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/res_users.xml',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        'views/data_views.xml',
        'views/hr_views.xml',
        'views/operation_views.xml',
        'views/structure_views.xml',
        'views/scale_views.xml',
        'views/mdc_config_settings.xml',
        'views/menuitem.xml',
        'views/templates.xml',
        'views/chkpoint_views.xml',
        'report/report_views.xml',
        'report/report_menuitem.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],

    'external_dependencies': {
        'python': [
            'requests',
            'websocket'
        ],
    }
}