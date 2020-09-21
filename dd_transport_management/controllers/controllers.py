# -*- coding: utf-8 -*-
from odoo import http

# class DdTransportManagement(http.Controller):
#     @http.route('/dd_transport_management/dd_transport_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dd_transport_management/dd_transport_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dd_transport_management.listing', {
#             'root': '/dd_transport_management/dd_transport_management',
#             'objects': http.request.env['dd_transport_management.dd_transport_management'].search([]),
#         })

#     @http.route('/dd_transport_management/dd_transport_management/objects/<model("dd_transport_management.dd_transport_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dd_transport_management.object', {
#             'object': obj
#         })