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
    'version': '0.1',

    'depends': ['base', 'product', 'hr', 'hr_contract', 'stock'],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/data_views.xml',
        'views/operation_views.xml',
        'views/structure_views.xml',
        'views/scale_views.xml',
        'views/menuitem.xml',
        'views/templates.xml',
        'data/structure_data.xml',
    ],

    'demo': [
        'demo/demo.xml',
    ],
}