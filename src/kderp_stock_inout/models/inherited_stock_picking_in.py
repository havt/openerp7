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
from openerp import tools

#
# Inherit of picking to add Info to Picking In
#
class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _name = 'stock.picking'

    def _default_location_source(self, cr, uid, context=None):
        """ Gets default Location Source if In -> Supplier
        @return: Location ID or False
        """
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        picking_type = context.get('picking_type')
        location_id = False

        location_xml_id = False
        if picking_type == 'in':
            location_xml_id = 'stock_location_suppliers'

        if location_xml_id:
            try:
                location_model, location_id = mod_obj.get_object_reference(cr, uid, 'stock', location_xml_id)
                with tools.mute_logger('openerp.osv.orm'):
                    self.pool.get('stock.location').check_access_rule(cr, uid, [location_id], 'read', context=context)
            except (orm.except_orm, ValueError):
                location_id = False

        return location_id

    _columns = {
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order',states={'done':[('readonly', True)], 'cancel':[('readonly',True)]},
                    ondelete='set null', select=True)
    }

    _defaults = {
                'purchase_id': lambda self, cr, uid, context: context.get('order_id', False) or context.get('purchase_id', False),
                'location_id': _default_location_source
                }