# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv, orm
from openerp import netsvc
from openerp import tools

import time
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _name="stock.move"
    
    _order = "purchase_line_id"
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.location_id and line.location_dest_id:
                name = line.location_id.name+' > '+line.location_dest_id.name
                # optional prefixes
                if line.product_id.code:
                    name = line.product_id.code + ': ' + name
                if line.picking_id.origin:
                    name = line.picking_id.origin + '/ ' + name
            else:
                name = line.product_id.code
            res.append((line.id, name))
        return res

    _columns = {
        #'product_id': fields.related('purchase_line_id','product_id', select=True, type="many2one", relation="product.product", string="Product",store=True),
                
        'purchase_line_id': fields.many2one('purchase.order.line',
            'Purchase Order Line', ondelete='restrict', select=True),
        'name': fields.char('Description', select=True),
        'date': fields.date('Date', required=True, select=True, help="Move date: scheduled date until move is done, then date of actual move processing", states={'done': [('readonly', True)]}),
        'date_expected': fields.date('Scheduled Date', states={'done': [('readonly', True)]},required=True, select=True, help="Scheduled date for the processing of this move"),

        'location_id': fields.many2one('stock.location', 'Source Warehouse', select=True,states={'done': [('readonly', True)]}, required=True),
        'location_dest_id': fields.many2one('stock.location', 'Destination Warehouse',states={'done': [('readonly', True)]}, required=True),

        'state': fields.selection([('draft', 'New'),
                                   ('cancel', 'Cancelled'),
                                   ('confirmed', 'Waiting for Delivery'),
                                   ('done', 'Done'),
                                   ], 'Status', readonly=True, select=True,
                                 help= "* New: When the stock move is created and not yet confirmed.\n"\
                                       "* Waiting for Delivery\n"\
                                       "* Done: When the shipment is processed, the state is \'Done\'."),
    }

    def _check_product_id(self, cr, uid, ids, context=None):
        """
            Kiem tra product id and purchase_line_id
        """
        if not context:
            context={}
        for sm in self.browse(cr, uid, ids, context=context):
            if sm.purchase_line_id and sm.product_id:
                if sm.purchase_line_id.product_id.id !=  sm.product_id.id:
                    return False
        return True
    
    _constraints = [(_check_product_id, 'KDERP Warning, Please Product and Purchase Line', ['purchase_line_id','product_id'])]
    
    def purchase_order_line_change(self, cr, uid, ids, order_line_id):        
        if not order_line_id:
            return {'value': {
                              'product_uos':False,
                              'product_id':False,
                              'product_uom':False}}
       
        for pol in self.pool.get('purchase.order.line').browse(cr,uid,[order_line_id]):
            if pol.product_id: 
                product_id = pol.product_id.id
            else:
                product_id=False
            prod_uom_po = pol.product_uom.id
            result={'value':{
            'product_id': product_id,
            'product_uom': prod_uom_po
            }}
        return result        
    
    def write(self, cr, uid, ids, vals, context = {}):
        list_check_ids = self.search(cr, uid, [('state','=','done'),('id','in', tuple(ids))])

        if 'state' in vals and vals['state']<>'done' and list_check_ids:
            for sm in self.browse(cr, uid, list_check_ids):
                check_period = self.pool.get('kderp.stock.period').check_period(cr, uid, sm.date, context)            
        return super(stock_move, self).write(cr, uid, ids, vals, context)
    
    def action_done(self, cr, uid, ids, context=None):
        """ Makes the move done and if all moves are done, it will finish the picking.
        @return:
        """
        picking_ids = []
        move_ids = []
        wf_service = netsvc.LocalService("workflow")
        if context is None:
            context = {}

        todo = []
        for move in self.browse(cr, uid, ids, context=context):
            if move.state=="draft":
                todo.append(move.id)
        if todo:
            self.action_confirm(cr, uid, todo, context=context)
            todo = []

        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ['done','cancel']:
                continue
            move_ids.append(move.id)

            if move.picking_id:
                picking_ids.append(move.picking_id.id)
            if move.move_dest_id.id and (move.state != 'done'):
                # Downstream move should only be triggered if this move is the last pending upstream move
                other_upstream_move_ids = self.search(cr, uid, [('id','!=',move.id),('state','not in',['done','cancel']),
                                            ('move_dest_id','=',move.move_dest_id.id)], context=context)
                if not other_upstream_move_ids:
                    self.write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})
                    if move.move_dest_id.state in ('waiting', 'confirmed'):
                        self.force_assign(cr, uid, [move.move_dest_id.id], context=context)
                        if move.move_dest_id.picking_id:
                            wf_service.trg_write(uid, 'stock.picking', move.move_dest_id.picking_id.id, cr)
                        if move.move_dest_id.auto_validate:
                            self.action_done(cr, uid, [move.move_dest_id.id], context=context)

            self._create_product_valuation_moves(cr, uid, move, context=context)
            if move.state not in ('confirmed','done','assigned'):
                todo.append(move.id)

        if todo:
            self.action_confirm(cr, uid, todo, context=context)
        date_received =  context.get('date_received',time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        
        self.write(cr, uid, move_ids, {'state': 'done', 'date': date_received}, context=context)
        
        check_period = self.pool.get('kderp.stock.period').check_period(cr, uid, date_received, context)
                
        for id in move_ids:
            wf_service.trg_trigger(uid, 'stock.move', id, cr)

        for pick_id in picking_ids:
            wf_service.trg_write(uid, 'stock.picking', pick_id, cr)

        return True

    # Revise move => draft others move and pickings
    #
    def action_cancel_draft(self, cr, uid, ids, context=None):
        """ Revise all the moves
        @return: True
        """
        if not len(ids):
            return True
        if context is None:
            context = {}

        self.write(cr, uid, ids, {'state': 'draft'})
        return True