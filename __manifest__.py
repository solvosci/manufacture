# -*- coding: utf-8 -*-
{
    'name': "slv_mdc",

    'summary': """
        SOLVOS manufacturing data control (MDC)""",

    'description': """
        SOLVOS manufacturing data control (MDC)
    """,

    'author': "Solvos Consultoría Informática",
    'website': "http://www.solvos.es",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'hr', 'hr_contract', 'stock'],

    # always loaded
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
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}