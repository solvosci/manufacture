# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Manufacturing data control: Add crumb cleaning checkpoint",
    "summary": """
        Crumb weighing data record before and after cleaning, 
        indicating shift, lot and employee. 
    """,
    "author": "Solvos",
    "license": "LGPL-3",
    "version": "11.0.1.0.1",
    "category": "Manufacturing",
    "website": "https://github.com/solvosci/manufacture",
    "depends": [
        'mdc'
    ],
    "data": [
        "security/ir.model.access.csv",
        'views/menuitem.xml',
        'views/data_views.xml',
        "views/chkpoint_views.xml",
        'views/operation_views.xml',
        "report/report_views.xml",
        "report/report_menuitem.xml",
    ],
    'installable': True,
}
