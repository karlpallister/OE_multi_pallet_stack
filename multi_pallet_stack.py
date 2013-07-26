# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv, fields

class pallet_types (osv.osv):
  _name = 'pallet.types'
	_columns = {
		'name': fields.char('Pallet Type', required=True, help='Pallet description'),
		'active': fields.boolean('Active'),
		'length': fields.integer('Length (mm)'),
		'width': fields.integer('Width (mm)'),
		'height': fields.integer('Height (mm)'),
		'weight': fields.integer('Weight (kg)')
		'product_id': fields.many2one('product.product', 'Pallet Product'),
		}
	_defaults = {
		'active': lambda *a, 1,
		}
	_sql_constraints = [('name_uniq', 'unique(name)', 'Pallet names must be unique!')]
pallet_types()

class pallet_stack_layout(osv.osv):

	_name = 'pallet.stack.layout'
    _columns = {
		'name': fields.char('Description', size=128, required=True),
		'active': fields.boolean('Active'),
		'program': fields.integer('Program Number', help='If this is stacked on a palletiser, this is the palletiser program number'),
		'pallet_type_id': fields.many2one('pallet.types','Pallet Type', ondelete='set null'),
		'layout_diagram': fields.binary('Layout diagram', filters='*.bmp,*.jpg,*.gif')
		'slipsheeted': fields.boolean('Slipsheeted', help='If product is stacked onto slipsheets, this box should be ticked.'),
		'layer_qty': fields.integer('Packages per layer'),
		'layer_height': fields.integer('Height per layer (mm)'),
		'layer_ids': fields.one2many('pallet_stack_layers', 'layout_id','Layer options'),
        }
	_defaults = {
		'active': lambda *a, 1,
		}
pallet_stack_layout()

class pallet_stack_layers(osv.osv):
	_name = 'pallet.stack.layers'
	#TODO This needs to calculate sum height of each layer and add the pallet height to come up with an overall height.
	#def _calc_total_height(self, cr, uid, ids, field_name, arg, context=None)
	
    _columns = {
		'name': fields.char('Description', size=128),
		'layout_id': fields.many2one('pallet.stack.layout', 'Pallet Stack Layout', ondelete='cascade'),
		'num_layers': fields.integer('Number of layers'),
		#'overall_height': fields.function(_calc_total_height, type='integer', string='Overall Height', store=True), 
        }
pallet_stack_layers()

class product_product(osv.osv)
	_name = 'product.product'
	_inherit = 'product.product'
	_columns = {
		'pallet_stack_layout_ids': fields.many2many('pallet_stack_layout', 'product_pallet_rel', 'product_id', 'pallet_stack_id', string='Possible pallet stacks'),
		'pallet_stack_layer_id': fields.many2one('pallet_stack_layers', 'Default layer quantity', domain=[('layout_id', 'in', 'pallet_stack_layout_ids')]),
		}
product_product()

class sale_order_line(osv.osv)
	_name = 'sale.order.line'
	_inherit = 'sale.order.line'
	_columns = {
		'sale_order_pallet_stack_ids': fields.one2many('sale.order.pallet.stack','Pallet Stack'), #TODO Filter to ids returned by product.product.pallet_stack_layers for the product
		}
sale_order_pallet_stack()

class sale_order_pallet_stack(osv.osv)
	_name = 'sale.order.pallet.stack'
	_columns = {
		'sale_order_line_id': fields.many2one('sale.order.line', 'Sales Order Line')
		'pallet_stack_id': fields.many2one('pallet.stack.layout','Pallet Stack'), #TODO Filter to ids returned by product.product.pallet_stack_layers for the product
		'num_layers': fields.many2one('pallet.stack.layers', 'Number of layers') #TODO Filter to ids returned by field above, and pre-enter default number of layers as a default.
		'num_pallets': fields.integer('Quantity of pallets')
		}
sale_order_pallet_stack()

#TODO create new BOM table inheriting from normal BOM, for pallet stacks - link to pallet_stack_layers
class mrp_bom_pallet(osv.osv)
	_name = 'mrp.bom.pallet'
	_inherits = 'mrp.bom'
mrp_bom_pallet()

#TODO on creation of Manufacturing Order, propogate pallet_stack_id, num_layers and num_pallets through to MO, and add relevant BOM items
class mrp_production(osv.osv)
	_name = 'mrp.production'
	_inherit = 'mrp.production'
	# Add Pallet BOM items in the def below
    def action_compute(self, cr, uid, ids, properties=None, context=None):
        """ Computes bills of material of a product.
        @param properties: List containing dictionaries of properties.
        @return: No. of products.
        """
        if properties is None:
            properties = []
        results = []
        bom_obj = self.pool.get('mrp.bom')
        uom_obj = self.pool.get('product.uom')
        prod_line_obj = self.pool.get('mrp.production.product.line')
        workcenter_line_obj = self.pool.get('mrp.production.workcenter.line')
        for production in self.browse(cr, uid, ids):
            cr.execute('delete from mrp_production_product_line where production_id=%s', (production.id,))
            cr.execute('delete from mrp_production_workcenter_line where production_id=%s', (production.id,))
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, production.product_id.id, production.product_uom.id, properties)
                if bom_id:
                    bom_point = bom_obj.browse(cr, uid, bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write(cr, uid, [production.id], {'bom_id': bom_id, 'routing_id': routing_id})

            if not bom_id:
                raise osv.except_osv(_('Error!'), _("Cannot find a bill of material for this product."))
            factor = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, bom_point.product_uom.id)
            res = bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, properties, routing_id=production.routing_id.id)
            results = res[0]
            results2 = res[1]
            for line in results:
                line['production_id'] = production.id
                prod_line_obj.create(cr, uid, line)
            for line in results2:
                line['production_id'] = production.id
                workcenter_line_obj.create(cr, uid, line)
        return len(results)
	_columns = {
		'pallet_stack_id': fields.many2one('pallet.stack.layout','Pallet Stack'), #TODO Filter to ids returned by product.product.pallet_stack_layers for the product
		'num_layers': fields.many2one('pallet.stack.layers', 'Number of layers') #TODO Filter to ids returned by field above, and pre-enter default number of layers as a default.
		'num_pallets': fields.integer('Quantity of pallets')
		}
mrp_production()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
