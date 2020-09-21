# -*- coding: utf-8 -*-
{
    'name': "dd_transport_management",

    'summary': """
        This module will help Transportation Owners 
        to manage vehicle reservations & tracking""",

    'description': """
        To integrate transport order to Sales Order and Billing System
    """,

    'author': "Smart",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'fleet',
                'purchase',
                'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/transport_groups.xml',
        'views/views.xml',
        'views/templates.xml',
        # 'views/transporter.xml', #this class for sourcing service
        'views/vehicle.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/menu.xml',
        'views/route_location.xml',
        'views/route_detail.xml',
        'views/transportation_product.xml',
        'views/transportation_route.xml',
        'views/transportation_service.xml',
        'views/transportation_order.xml',
        'views/transportation_entry.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}