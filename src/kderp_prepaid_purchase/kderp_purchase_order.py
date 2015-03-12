# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2013 Tiny SPRL (<http://tiny.be>).
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

# class purchase_order(osv.osv):
#     """
#         Add new field link Prepaid Order to Purchase Order
#     """
#     _name = 'purchase.order'
#     _inherit = 'purchase.order'
#     _description = 'KDERP Prepaid Purchase Order'
#     
#     def unlink(self, cr, uid, ids, context=None):
#         for ppo in self.browse(cr, uid, ids):
#             if ppo.state<>'draft':
#                 raise osv.except_osv(_('Error!'), _('You can remove a Prepaid Purchase with state is Draft only'))
#         return super(kderp_prepaid_purchase_order, self).unlink(cr, uid, ids, context=context)
#     
#     def name_get(self, cr, uid, ids, context=None):
#         if not context: context={}
#         res=[]
#         for record in self.browse(cr, uid, ids):
#             name = "%s - %s" % (record.name, record.description)  
#             res.append((record['id'], name))
#         return res
#     
#     def action_draft_to_approved(self, cr, uid, ids, context = {}):
#         val = {'state':'approved'}
#         self.write(cr, uid, ids, val, context)   
#         picking_ids = []
#         for order in self.browse(cr, uid, ids):
#             picking_ids.extend(self._create_pickings(cr, uid, order, order.prepaid_order_line, None, context=context))
# 
#         # Must return one unique picking ID: the one to connect in the subflow of the purchase order.
#         # In case of multiple (split) pickings, we should return the ID of the critical one, i.e. the
#         # one that should trigger the advancement of the purchase workflow.
#         # By default we will consider the first one as most important, but this behavior can be overridden.
#         return picking_ids[0] if picking_ids else False
#     
#     def action_reject(self, cr, uid, ids, context = {}):
#         if not context:
#             context = {}
#         for ppo in self.browse(cr, uid, ids, context):
#             for pk in ppo.packing_ids:
#                 if pk not in ('draft','cancel'):
#                     raise osv.except_osv("KDERP Warning", "State in packing related not in draft")
#         self.write(cr, uid, ids, {'state''cancel'})
#         return True
#     
#     SELECTION_STATE = [('draft','Draft'),
#                        ('approved','Approved'),
#                        ('done','Done'),
#                        ('cancel','Rejected')]
#     
#     def onchange_date(self, cr, uid, ids, oldno, date):
#         val = {}
#         if not oldno and date:
#             cr.execute("""SELECT 
#                             wnewcode.pattern || 
#                             btrim(to_char(max(substring(wnewcode.code::text, length(wnewcode.pattern) + 1,padding )::integer) + 1,lpad('0',padding,'0'))) AS newcode
#                         from
#                             (
#                             SELECT 
#                                 isq.name,
#                                 isq.code as seq_code,
#                                 isq.prefix || to_char(DATE '%s', suffix || lpad('_',padding,'_')) AS to_char, 
#                                 CASE WHEN cnewcode.code IS NULL 
#                                 THEN isq.prefix::text || to_char(DATE '%s', suffix || lpad('0',padding,'0'))
#                                 ELSE cnewcode.code
#                                 END AS code, 
#                                 isq.prefix::text || to_char(DATE '%s', suffix) AS pattern,
#                                 padding,
#                                 prefix
#                             FROM 
#                                 ir_sequence isq
#                             LEFT JOIN 
#                                 (SELECT 
#                                     kderp_prepaid_purchase_order.name as code
#                                 FROM 
#                                     kderp_prepaid_purchase_order
#                                 WHERE
#                                     length(kderp_prepaid_purchase_order.name::text)=
#                                     ((SELECT 
#                                     length(prefix || suffix) + padding AS length
#                                     FROM 
#                                     ir_sequence
#                                     WHERE 
#                                     ir_sequence.code::text = 'kderp_prepaid_order_code'::text LIMIT 1))
#                                 ) cnewcode ON cnewcode.code::text ~~ (isq.prefix || to_char(DATE '%s',  suffix || lpad('_',padding,'_'))) and isq.code::text = 'kderp_prepaid_order_code'::text  
#                             WHERE isq.active and isq.code::text = 'kderp_prepaid_order_code') wnewcode
#                         GROUP BY 
#                             pattern, 
#                             name,
#                             seq_code,
#                             prefix,
#                             padding""" %(date,date,date,date))
#             res = cr.fetchone()
#             if res:
#                 val={'name':res[0]}
#         
#         return {'value':val}
#     
#     _order="date desc, name desc"
#     _columns={
#               'name':fields.char('Code', required = True, size=16, select=1, readonly = True, states={'draft':[('readonly', False)]}),
#               'description':fields.char('Description', required = True, size=64, readonly = True, states={'draft':[('readonly', False)]}),
#               'date':fields.date('Order Date', select = 1, required = True, readonly = True, states={'draft':[('readonly', False)]}),
#               
#               'partner_id':fields.many2one('res.partner', 'Supplier', ondelete='restrict', required=True, readonly = True, states={'draft':[('readonly', False)]} , change_default=True),
#               'address_id':fields.many2one('res.partner', 'Address', ondelete='restrict', required=True, readonly = True, states={'draft':[('readonly', False)]}),
#               'currency_id':fields.many2one('res.currency','Curr', required=True, readonly = True, states={'draft':[('readonly', False)]}),
#               
#               'packing_ids':fields.one2many('stock.picking','prepaid_purchase_order_id','Packing List', readonly = True),
#               
#               'prepaid_order_line':fields.one2many('kderp.prepaid.purchase.order.line', 'prepaid_order_id', readonly = True, states={'draft':[('readonly', False)]}),
# 
#               'state':fields.selection(SELECTION_STATE, 'State', readonly = True)
#               }
#     
#     _defaults = {
#                  'date': lambda *a: time.strftime('%Y-%m-%d'),
#                  'state': lambda *x: 'draft',
#                  'partner_id':lambda self, cr, uid, context={}: context.get('partner_id',False),
#                  'currency_id':lambda self, cr, uid, context={}:self.pool.get('res.users').browse(cr, uid, uid).company_id.currency_id.id
#                  }
#     
#     _sql_constraints=[('kderp_prepaid_purchase_code_unique','unique(code)','Prepaid Purchase Code must be unique !')]
#     
#     def onchange_partner_id(self, cr, uid, ids, partner_id):
#         partner = self.pool.get('res.partner')
#         if not partner_id:
#             return {'value': {
#                 'fiscal_position': False,
#                 'payment_term_id': False,
#                 }}
#         supplier_address = partner.address_get(cr, uid, [partner_id], ['default'])
#         supplier = partner.browse(cr, uid, partner_id)
#         return {'value': {'address_id': supplier.id or False }}
#     
#     #Stock Picking and MoveArea
#     def date_to_datetime(self, cr, uid, userdate, context=None):
#         """ Convert date values expressed in user's timezone to
#         server-side UTC timestamp, assuming a default arbitrary
#         time of 12:00 AM - because a time is needed.
#     
#         :param str userdate: date string in in user time zone
#         :return: UTC datetime string for server-side use
#         """
#         from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
#         # TODO: move to fields.datetime in server after 7.0
#         user_date = datetime.strptime(userdate, DEFAULT_SERVER_DATE_FORMAT)
#         if context and context.get('tz'):
#             tz_name = context['tz']
#         else:
#             tz_name = self.pool.get('res.users').read(cr, SUPERUSER_ID, uid, ['tz'])['tz']
#         if tz_name:
#             utc = pytz.timezone('UTC')
#             context_tz = pytz.timezone(tz_name)
#             user_datetime = user_date + relativedelta(hours=12.0)
#             local_timestamp = context_tz.localize(user_datetime, is_dst=False)
#             user_datetime = local_timestamp.astimezone(utc)
#             return user_datetime.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#         return user_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#     
#     def _prepare_order_picking(self, cr, uid, order, context=None):
#         return {
#             'name': self.pool.get('ir.sequence').get(cr, uid, 'stock.picking.in'),
#             'origin': order.name,
#             'date': self.date_to_datetime(cr, uid, order.date, context),
#             'partner_id': order.partner_id.id,
#             'invoice_state': 'none', 
#             'type': 'in',
#             'prepaid_purchase_order_id': order.id,
#             #'company_id': order.company_id.id,
#             'move_lines' : [],
#         }
#     
#     def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
#         price_unit = order_line.price_unit
# #        if order.currency_id.id != order.company_id.currency_id.id:
#             #we don't round the price_unit, as we may want to store the standard price with more digits than allowed by the currency
# #            price_unit = self.pool.get('res.currency').compute(cr, uid, order.currency_id.id, order.company_id.currency_id.id, price_unit, round=False, context=context)
#         return {
#             'name': order_line.name or '',
#             'product_id': order_line.product_id.id,
#             'product_qty': order_line.product_qty,
#             'product_uos_qty': order_line.product_qty,
#             'product_uom': order_line.product_uom.id,
#             'product_uos': order_line.product_uom.id,
#             'date': self.date_to_datetime(cr, uid, order.date, context),
#             #'date_expected': self.date_to_datetime(cr, uid, order_line.date_planned, context),
#             'location_id': order.partner_id.property_stock_supplier.id,
#             'location_dest_id': order_line.location_id.id,
#             'picking_id': picking_id,
#             'partner_id': order.partner_id.id,
#             #'move_dest_id': order_line.move_dest_id.id,
#             'state': 'draft',
#             'type':'in',
#             'prepaid_purchase_line_id': order_line.id,
#             #'company_id': order.company_id.id,
#             'price_unit': price_unit
#         }     
#     
#     def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None):
#         """Creates pickings and appropriate stock moves for given order lines, then
#         confirms the moves, makes them available, and confirms the picking.
# 
#         If ``picking_id`` is provided, the stock moves will be added to it, otherwise
#         a standard outgoing picking will be created to wrap the stock moves, as returned
#         by :meth:`~._prepare_order_picking`.
# 
#         Modules that wish to customize the procurements or partition the stock moves over
#         multiple stock pickings may override this method and call ``super()`` with
#         different subsets of ``order_lines`` and/or preset ``picking_id`` values.
# 
#         :param browse_record order: purchase order to which the order lines belong
#         :param list(browse_record) order_lines: purchase order line records for which picking
#                                                 and moves should be created.
#         :param int picking_id: optional ID of a stock picking to which the created stock moves
#                                will be added. A new picking will be created if omitted.
#         :return: list of IDs of pickings used/created for the given order lines (usually just one)
#         """
#         if not picking_id:
#             picking_id = self.pool.get('stock.picking').create(cr, uid, self._prepare_order_picking(cr, uid, order, context=context))
#         todo_moves = []
#         stock_move = self.pool.get('stock.move')
#         wf_service = netsvc.LocalService("workflow")
#         for order_line in order_lines:
#             if not order_line.product_id:
#                 continue
#             if order_line.product_id.type in ('product', 'consu'):
#                 move = stock_move.create(cr, uid, self._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context))
#                 #if order_line.move_dest_id and order_line.move_dest_id.state != 'done':
#                 #    order_line.move_dest_id.write({'location_id': order.location_id.id})
#                 todo_moves.append(move)
#         stock_move.action_confirm(cr, uid, todo_moves)
#         stock_move.force_assign(cr, uid, todo_moves)
#         wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
#         return [picking_id]
# 
#     def action_picking_create(self, cr, uid, ids, context=None):
#         picking_ids = []
#         for order in self.browse(cr, uid, ids):
#             picking_ids.extend(self._create_pickings(cr, uid, order, order.prepaid_order_line, None, context=context))
# 
#         # Must return one unique picking ID: the one to connect in the subflow of the purchase order.
#         # In case of multiple (split) pickings, we should return the ID of the critical one, i.e. the
#         # one that should trigger the advancement of the purchase workflow.
#         # By default we will consider the first one as most important, but this behavior can be overridden.
#         return picking_ids[0] if picking_ids else False
#     
# purchase_order()

class purchase_order_line(osv.osv):
    """
        Add new field link Prepaid Order to Purchase Order Line
    """
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'
    
    _columns = {
                'prepaid_purchase_order_line_id':fields.many2one('kderp.prepaid.purchase.order.line','Prepaid Order Line',ondelete='restrict')
                }
    