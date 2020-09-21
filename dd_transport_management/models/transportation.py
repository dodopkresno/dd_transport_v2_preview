# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

# class dd_transport_management(models.Model):
#     _name = 'dd_transport_management.dd_transport_management'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

# this class use for sourcing service
# class Transporter(models.Model):
#     _inherit = 'res.partner'

#     is_transporter = fields.Boolean(string='Is Transporter?', default=False)

class Vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    is_service = fields.Boolean(string='As a Service?')
    partner_ref = fields.Many2one(
        string='Partner Ref.',
        comodel_name='res.partner',
    )
    max_weight = fields.Float(string='Max. Weight')
    max_volume = fields.Float(string='Max. Volume')

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    service_id = fields.Many2one(
        string='Service Order',
        comodel_name='transportation.service',
    )
    state = fields.Selection(
        selection_add=[('verified', 'To Approve'),
                        ('appr','Approved'),]
    )

    @api.multi
    def action_verify(self):
        for rec in self:
            if rec.service_id:
                if rec.service_id.state != 'complete':
                    raise ValidationError(_(''' Cannot verified this SO, due to transportation service not completed yet!!! '''))
                else:
                    rec.state='verified'

    @api.one
    def action_back_verify(self):
        self.state='draft'

    @api.one
    def action_approved(self):
        self.state='appr'

class SaleOrder(models.Model):
    _inherit = 'sale.order' 

    trans_order_id = fields.Many2one(
        string='Transport Order',
        comodel_name='transportation.order',
    )
    state = fields.Selection(
        selection_add=[('verified', 'To Approve'),
                    ('appr','Approved'),]
        )
    
    @api.multi
    def action_verify(self):
        for rec in self:
            if rec.trans_order_id:
                if rec.trans_order_id.state != 'pod':
                    raise ValidationError(_(''' Cannot verified this SO, due to transportation order not POD yet!!! '''))
                else:
                    rec.state='verified'

    @api.one
    def action_back_verify(self):
        self.state='draft'

    @api.one
    def action_approved(self):
        self.state='appr'
    
class RouteLocation(models.Model):
    _name = 'route.location'
    _rec_name = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )
    code = fields.Char(
        string='Reference',
        required=True,
    )
    _sql_constraints = [('ref_code_unique','unique (code)','Code must be unique!!!')]

class RouteDetail(models.Model):
    _name = 'route.detail'
    _description = 'This will manage From-To Route'
    
    transport_route_id = fields.Many2one(
        string='Transport Route',
        comodel_name='transportation.route',
        required=True,
    )
    origin = fields.Many2one(
        string='Origin',
        comodel_name='route.location',
        required=True,
    )
    destination = fields.Many2one(
        string='Destination',
        comodel_name='route.location', 
        required=True,
    )
    distance = fields.Float(
        string='Distance(Km)',
        help='Distance in Kilometer',
        digits=(6,2)
    )
    hour = fields.Float(
        string='Hour(s)',
    )

    @api.constrains('destination')
    def _check_ori_dest(self):
        r_destination = self.search([("destination","=",self.destination.id),
                                ("origin","=",self.origin.id),
                                ("id","not in", self.ids)])
        if r_destination:
            raise ValidationError(_('''The origin and destination that you entered 
                                    already exist. Please enter the new one!'''))

class TransportationRoute(models.Model):
    _name = 'transportation.route'
    _description = 'This will manage route of the transportation provider'
    _rec_name = 'name'
    
    code = fields.Char(
        string='Reference',
        required=True,
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    is_active = fields.Boolean(
        string='Is Active?', 
        default=True,
    )
    route_detail_ids = fields.One2many(
        string='Route Detail',
        comodel_name='route.detail',
        inverse_name='transport_route_id',
    )
    product_ids = fields.One2many(
        string='Transport Fees',
        comodel_name='transportation.product',
        inverse_name='transport_route_id',
    )
    
    @api.constrains('code')
    def _check_code(self):
        trx_code = self.search([("code","=",self.code),
                                ("id","not in", self.ids)])
        if trx_code:
            raise ValidationError(_('''The code that you entered 
                                    already exist. Please enter difference code!'''))

class TransportationProduct(models.Model):
    _name = 'transportation.product'
    _description = 'this module for manage transportation service fees'
    
    vehicle_type_tag_id = fields.Many2one(
        string='Vehicle Type',
        comodel_name='fleet.vehicle.tag',
        required=True,
    )
    vehicle_owner_tag_id = fields.Many2one(
        string='Owner Status',
        comodel_name='fleet.vehicle.tag',
        required=True,
    )
    transport_route_id = fields.Many2one(
        string='Route Ref.',
        comodel_name='transportation.route',
        required=True,
    )
    product_id = fields.Many2one(
        string='Product Ref.',
        comodel_name='product.product',
        required=True,
    )
    transport_fees = fields.Float(
        string='Services Fees',
        digits=(6,2),
        related='product_id.list_price',
        store=True,
    )
   
    @api.constrains('product_id')
    def _check_product_id(self):
        c_product_id = self.search([('product_id','=',self.product_id.id),
                                    ('id','not in', self.ids)])
        if c_product_id:
            raise ValidationError(_('''The product service you have entered already exist.
                                    Please choose difference service code!'''))

class TransportationService(models.Model):
    _name = 'transportation.service'
    _inherit = 'mail.thread'
    #_rec_name = 'vehicle_id'

    name = fields.Char(
        string='Reference',
        required=True,
    )
    vehicle_id = fields.Many2one(
        string='Vehicle Ref.',
        comodel_name='fleet.vehicle',     
        required=True,
    )
    driver_name = fields.Char(
        string='Driver Name',
        related='vehicle_id.driver_id.name', 
        store=False,        
    )
    lic_plate = fields.Char(
        string='Plate Lic.',
        related='vehicle_id.license_plate',
        readonly=True,
    )
    max_weight = fields.Float(
        string='Max.Weight',
        related='vehicle_id.max_weight',
        digits=(6,2),
        readonly=True,
    )
    max_volume = fields.Float(
        string='Max.Volume',
        related='vehicle_id.max_volume',
        digits=(6,2),
        readonly=True,
    )
    product_id = fields.Many2one(
        string='Order Product',
        comodel_name='product.product',
    )
    is_sourcing = fields.Boolean(
        string='Is Sourcing',
    )
    order_count = fields.Integer(
        string='# Order',
        compute='_order_count'
    )
    po_count = fields.Integer(
        string='# Purchase',
        compute='_vendor_order_count'
    )
    util_weight = fields.Float(
        string='Weight.Utilization',
        readonly=True,
    )
    util_volume = fields.Float(
        string='Vol.Utilization',
        readonly=True,
    )
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                ('open', 'Open'),
                ('reserve', 'Reserve'),#trigger while transport order is approve
                ('ontrip', 'On Trip'),#works
                ('complete', 'Complete'),
                ('cancel', 'Cancel'),
                ],
        readonly=True,
        default='draft',
        track_visibility='onchange',
    )
    
    @api.multi  
    def name_get(self):
        return [(this.id, this.vehicle_id.name + "#" + " " + this.name) for this in self]
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ['reserve','ontrip','complete']:
                raise ValidationError(_('''Cannot delete this record, please check your related transaction'''))
            
            obj_order = self.env['transportation.order'].search([('service_id','=',rec.id)], limit=1)
            if obj_order:
                 raise ValidationError(_('''Cannot delete this record, please check your related transaction'''))
        
        return super(TransportationService, self).unlink()

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            for rec in self.vehicle_id.tag_ids:
                if rec.name.upper() == 'SOURCING':
                    self.is_sourcing = True
                else:
                    self.is_sourcing = False

            #self.is_sourcing = flag
            #return {'value': {'is_sourcing': flag}}
    
    @api.multi
    def _order_count(self):
        to_order_ids = self.env['transportation.order'].search([('service_id','=',self.id)])
        self.order_count = len(to_order_ids)
    
    @api.multi
    def action_view_transport_order(self):
        to_order_obj = self.env['transportation.order'].search([('service_id','=',self.id)])
        order_ids = []
        for each in to_order_obj:
            order_ids.append(each.id)
        view_id = self.env.ref('dd_transport_management.transportation_order_form').id
        if order_ids:
            if len(order_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'transportation.order',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Orders'),
                    'res_id': order_ids and order_ids[0]
                }
            else:
                value = {
                    'domain': str([('id','in',order_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'transportation.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Order'),
                    'res_id': order_ids
                }
            return value
    
    @api.multi
    def _vendor_order_count(self):
        po_service_ids = self.env['purchase.order'].search([('service_id','=',self.id)])
        self.po_count = len(po_service_ids)
    
    @api.multi
    def action_view_purchase_order(self):
        to_porder_obj = self.env['purchase.order'].search([('service_id','=',self.id)])
        order_ids = []
        for each in to_porder_obj:
            order_ids.append(each.id)
        view_id = self.env.ref('purchase.purchase_order_form').id
        if order_ids:
            if len(order_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'purchase.order',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Order'),
                    'res_id': order_ids and order_ids[0]
                }
            else:
                value = {
                    'domain': str([('id','in',order_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'purchase.order',
                    'view_id': false,
                    'type': 'ir.actions.act_window',
                    'name': _('Order'),
                    'res_id': order_ids
                }
            return value

    @api.multi
    def generate_vendor_order(self):
        purchase_obj = self.env['purchase.order'].create(
            {'partner_id': self.vehicle_id.partner_ref.id,
             'date_order': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

        self.p_order = purchase_obj
        supp_inv_obj = self.env['product.supplierinfo'] #get sourcing price
        p_vendor_price = supp_inv_obj.search([('id','=', self.vehicle_id.partner_ref.id)]).price
        purch_line_obj = self.env['purchase.order.line'].create(
            {'product_id':self.product_id.id,
             'name':self.product_id.partner_ref,
             'order_id':purchase_obj.id,
             'product_qty':1,
             'price_unit':p_vendor_price})
        #set state on IH_PO to Pending

    @api.multi
    def update_utilization(self):
        to_obj = self.env['transportation.order']
        data_ids = to_obj.search([('service_id','=',self.id)])
        if data_ids:
            sum_weight = 0
            sum_volume = 0
            for rec in data_ids:
                sum_weight += rec.to_total_weight
                sum_volume += rec.to_total_volume
            
            if self.max_weight > 0:
                self.util_weight = 100.0 * sum_weight/self.max_weight
            else:
                self.util_weight = 0.0
            
            if self.max_volume > 0:
                self.util_volume = 100.0 * sum_volume/self.max_volume
            else:
                self.util_volume = 0.0

    @api.constrains('name')
    def _check_name(self):
        iname = self.search([('name','=',self.name),
                            ('id','not in', self.ids)])
        if iname:
            raise ValidationError(_(''' Name Reference you have entered already exist.
                                    Please choose difference name!'''))

    @api.multi
    def action_open(self):
        self.state = 'open'    
    
    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

class TransportationOrder(models.Model):
    _name = 'transportation.order'
    
    name = fields.Char(
        string='Reference',
        default='/',
        readonly=True,)
    service_id = fields.Many2one(
        string='Service No',
        comodel_name='transportation.service',)
    customer_id = fields.Many2one(
        string='Customer Name',
        comodel_name='res.partner',
        required=True,)
    route_id = fields.Many2one(
        string='Route(s)',
        comodel_name='transportation.route',)
    product_id = fields.Many2one(
        string='Service Type',
        comodel_name='product.product',)
    so_count = fields.Integer(
        string='# Sale Order',
        compute='_sale_order_count'
    )
    to_name = fields.Char(
        string='Consignee',
        required=True,
    )
    to_phone = fields.Char(
        string='Phone',
    )
    to_address = fields.Text(
        string='Address',
    )
    to_parcel = fields.Char(
        string='Parcel',
    )
    to_uom = fields.Char(
        string='UoM',
    )
    to_qty = fields.Integer(
        string='Qty',
    )
    to_total_weight = fields.Float(
        string='Total Weight',
        required=True,
    )
    to_total_volume = fields.Float(
        string='Total Volume',
        required=True,
    )
    notes = fields.Text(
        string='Note',)
    entry_ids = fields.One2many(
        string='Transport Entries',
        comodel_name='transportation.entry',
        inverse_name='order_id',
    )
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), 
                    ('appr','Approve'), #-->trigger service generate PO for sourcing, SO for owned
                    ('inprg', 'In Progress'), #--> trigger generate entry
                    ('pod','POD')],
                    readonly=True,
        default='draft',
        track_visibility='onchange',
    )

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('transportation.order')
        result = super(TransportationOrder, self).create(vals)
        return result

    #get product based on route
    @api.onchange('route_id')
    def _onchange_route_id(self):
        if self.route_id:
            product_list = []
            for rec in self.route_id.product_ids:
                product_list.append(rec.product_id.id)

            return {
                'domain': {
                    'product_id': [('id', 'in', product_list)]
                }
            }

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            t_product_obj = self.env['transportation.product']
            t_service_obj = self.env['transportation.service']
            t_fleet_veh = self.env['fleet.vehicle']
            service_id_list = []

            data = t_product_obj.search([('product_id','=', self.product_id.id)])
            if data.vehicle_owner_tag_id.name.upper() == 'SOURCING':
                service_ids = t_service_obj.search([('is_sourcing','=',True),('state','=','open')])
            else:
                service_ids = t_service_obj.search([('is_sourcing','=',False),('state','=','open')])
            
            if service_ids :
                for each in service_ids:
                    service_id_list.append(each.id)

                return {
                    'domain': {
                        'service_id': [('id', 'in', service_id_list)]
                        }
                }
            else:
                raise ValidationError(_('''No Service Available for this Route!'''))

    @api.multi
    def confirm_approve(self):
        self.state = 'appr'
        
        if self.service_id:
            sale_obj = self.env['sale.order'].create(
                    {'partner_id': self.customer_id.id,
                     'trans_order_id': self.id,
                     'date_order': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            self.s_order = sale_obj
            sale_line_obj = self.env['sale.order.line'].create(
                {'order_id':sale_obj.id,
                 'product_id':self.product_id.id,
                 'name':self.product_id.partner_ref,
                 'product_uom_qty': 1,
                 'price_unit':self.product_id.list_price})
            #set state on IH_SO to Pending
            
            self.service_id.state = 'reserve'
        else:
            raise ValidationError(_('''Cannot change state to approve, 
                                please choose service order first!'''))
    
    @api.multi
    def action_inprogress(self):
        self.state = 'inprg'
        obj_route_detail = self.env['route.detail']
        for rec in self.route_id.route_detail_ids:
            data = obj_route_detail.search([('id','=',rec.id)])
            trans_entry_obj = self.env['transportation.entry'].create(
                {'order_id':self.id,
                 'origin_id':rec.origin.id,
                 'destination_id':rec.destination.id,
                 'distance':data.distance,
                 'hour':data.hour,
                 'state':'draft'
                })
    
    @api.multi
    def _sale_order_count(self):
        so_service_ids = self.env['sale.order'].search([('trans_order_id','=',self.id)])
        self.so_count = len(so_service_ids)
    
    @api.multi
    def action_view_sale_order(self):
        to_sorder_obj = self.env['sale.order'].search([('trans_order_id','=',self.id)])
        order_ids = []
        for each in to_sorder_obj:
            order_ids.append(each.id)
        view_id = self.env.ref('sale.view_order_form').id
        if order_ids:
            if len(order_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Order'),
                    'res_id': order_ids and order_ids[0]
                }
            else:
                value = {
                    'domain': str([('id','in',order_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': false,
                    'type': 'ir.actions.act_window',
                    'name': _('Order'),
                    'res_id': order_ids
                }
            return value
        
    @api.multi
    def action_confirm_pod(self):
        flag_comp = self.entry_ids.search([('state','!=','complete')])
        if flag_comp:
            raise ValidationError(_('''Cannot change state to POD, 
                                due to any entry not completed!'''))
        else:
            self.state = 'pod'

class TransportationEntry(models.Model):
    _name = 'transportation.entry'
    _inherit = 'mail.thread'
    
    order_id = fields.Many2one(
        string='Transportation Order',
        comodel_name='transportation.order',
        readonly=True,)
    service_name = fields.Char(
        string='Service',
        related='order_id.service_id.name',
        readonly=True,
        )
    vehicle_name = fields.Char(
        string='Vehicle',
        related='order_id.service_id.vehicle_id.name',
        readonly=True,
        )
    origin_id = fields.Many2one(
        string='Origin',
        comodel_name='route.location',
        readonly=True,)
    destination_id = fields.Many2one(
        string='Destination',
        comodel_name='route.location',
        readonly=True,)
    distance = fields.Float(
        string='Theoretical Distance',
        digits=(16, 2),
        readonly=True,)
    hour = fields.Float(
        string='Theoretical Hour(s)',
        readonly=True,)
    actual_hour = fields.Float(
        string='Actual Hour(s)',)
    actual_distance = fields.Float(
        string='Actual Distance',)
    start_time = fields.Datetime(
        string='Start',)
    start_loading = fields.Datetime(
        string='Start Loading',)
    end_loading = fields.Datetime(
        string='End Loading',)
    start_unloading = fields.Datetime(
        string='Start Unloading',)
    end_unloading = fields.Datetime(
        string='End Unloading',)
    gps_tracking = fields.Char(
        string='GPS No.',)
    notes = fields.Text(
        string='Note',)
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'),
                ('start','Start'), 
                ('onloading', 'On Loading'),
                ('ondelivery','On Delivery'),
                ('onunload','On Unloading'),
                ('complete','Complete')], 
                default='draft', 
                track_visibility='onchange', 
                readonly=True,)

    @api.multi
    def action_start(self):
        for rec in self:
            rec.start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.state = 'start'
    
    @api.multi
    def action_load(self):
        for rec in self:
            rec.start_loading = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.state = 'onloading'
    
    @api.multi
    def action_delivery(self):
        for rec in self:
            rec.end_loading = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.state = 'ondelivery'
    
    @api.multi
    def action_unload(self):
        for rec in self:
            rec.start_unloading = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.state = 'onunload'
    
    @api.multi
    def action_complete(self):
        for rec in self:
            rec.end_unloading = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.state = 'complete'