from openerp.osv.orm import Model
from openerp.osv import fields, osv

import openerp.addons.decimal_precision as dp
import re

class sale_order(Model):
    _inherit = 'sale.order'

    STATE_SELECTION=[('draft', 'Not yet decided'),
                    ('done', 'Work Received'),
                    ('cancel', 'Cancelled')]
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] =  val
            res[order.id]['amount_untaxed'] =  val1
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res
    
    def _get_quotation_total(self, cr, uid, ids, name, args, context=None):
        res={}
        for quo in self.browse(cr,uid,ids):
            res[quo.id] = (quo.q_prj_budget_amount_e or 0.0) + (quo.q_prj_budget_amount_m or 0.0)
        return res
    
    def _get_sort_state(self, cr, uid, ids, field_name, arg, context):
        res = {}
        if ids:
            quo_ids = ",".join(map(str,ids))
            cr.execute("""Select \
                            id,case when state='done' then 1 else case when state='draft' then 2 else 3 end end as sort_status\
                        from sale_order where id in (%s)""" % quo_ids)
            for id,re in cr.fetchall():
                res[id] = re
        return res
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if not context:
            context={}
        payment_client_ids = context.get("kderp_search_default_quotation_client_lists",[])
        if payment_client_ids:
            quo_ids=[]
            for payment_client in self.pool.get('account.invoice').browse(cr, uid, payment_client_ids):
                for so in payment_client.contract_id.quotation_ids:
                    quo_ids.append(so.id)
            args.append((('id', 'in',  quo_ids)))        
        return super(sale_order, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=False)
    
    def _get_quotation_attachment(self, cr, uid, ids, name, arg, context=None):
        res = {}
        if ids:
            so_id_list = ",".join(map(str,ids))
            cr.execute("""Select
                           so.id as id,
                           case when sum(case when coalesce(ia.q_attached,False) then 1 else 0 end) >0 then 1 else 0 end as q_attached,
                           case when sum(case when coalesce(ia.q_attached_be,False) then 1 else 0 end) >0 then 1 else 0 end as q_attached_be,
                           case when sum(case when coalesce(ia.q_attached_bm,False) then 1 else 0 end)>0 then 1 else 0 end as q_attached_bm,
                           case when sum(case when coalesce(ia.q_attached_je,False) then 1 else 0 end) >0 then 1 else 0 end as q_attached_je,
                           case when sum(case when coalesce(ia.q_attached_jm,False) then 1 else 0 end) >0 then 1 else 0 end as q_attached_jm,
                           case when sum(case when coalesce(ia.q_attached_jcombine,False) then 1 else 0 end) >0 then 1 else 0 end as q_attached_jcombine,
                           case when sum(case when coalesce(ia.q_attached_qcombine,False) then 1 else 0 end) >0 then 1 else 0 end as q_attached_qcombine
                       from
                           sale_order so
                       left join
                           ir_attachment ia on so.id=ia.res_id and res_model='sale.order'
                       where
                           so.id in (%s) 
                       group by 
                            so.id""" % (so_id_list))
            for sol in cr.dictfetchall():
                res[sol.pop('id')]=sol
        return res
    
    def _get_attachement_link(self, cr, uid, ids, context=None):
        res={}
        for att_obj in self.pool.get('ir.attachment').browse(cr,uid,ids):
            if att_obj.res_model=='sale.order' and att_obj.res_id:
                res[att_obj.res_id] = True
        return res.keys()

    def _get_quoation_approved_info(self, cr, uid, ids, name, arg, context=None):
        res={}
        for so in self.browse(cr, uid, ids):
            res[so.id]={'currencies':False,
                        'approved_amount_e':0,
                        'approved_amount_m':0,
                        'total_approved_amount':0.0
                        }
             
            for sol in so.order_line:
                res[so.id]['currencies']=sol.currency_id.id
                res[so.id]['approved_amount_e']=sol.price_unit+sol.discount
                res[so.id]['total_approved_amount']=sol.price_unit+sol.discount
                
            for sol in so.order_line_m:
                res[so.id]['currencies']=sol.currency_id.id
                res[so.id]['approved_amount_m']=sol.price_unit+sol.discount
                res[so.id]['total_approved_amount']+=sol.price_unit+sol.discount
                
            
        return res
    
    def _get_negotiating(self, cr, uid, ids, name, arg, context=None):
        res={}
        so_ids=",".join(map(str,ids))
        cr.execute("""Select
                        so.id,
                        case when sum(coalesce(price_unit,0))<>0 then 'Fixed' else 'Negotiated' end
                    from 
                        sale_order so
                    left join
                        sale_order_line sol on so.id=sol.order_id
                    where
                        so.id in (%s)
                    group by
                        so.id
                        """ % (so_ids))
        for so_id,re in cr.fetchall():
            res[so_id]=re
        return res
    
    def _get_completion_date_contract(self, cr, uid, ids, name, args, context=None):
        res = {}
        if ids:
            quo_ids = ",".join(map(str,ids))
            cr.execute("""SELECT so.id ,kcc.completion_date AS completion_date_contract
                           FROM sale_order so
                           LEFT JOIN kderp_contract_client kcc ON so.contract_id = kcc.id where so.id in (%s)""" % (quo_ids))
            for id,completion_date_contract in cr.fetchall():
                res[id] = completion_date_contract
        return res
    
    def _get_max_completion(self, cr, uid, ids, name, args, context=None):
        res = {}
        if ids:
            quo_ids = ",".join(map(str,ids))
            cr.execute("""SELECT 
                            so.id,
                            coalesce(case when 
                                kcc.completion_date>so.completion_date or so.completion_date is null 
                            then
                                kcc.completion_date
                            else
                                so.completion_date
                            end,'2199/12/31') as max_completion_date
                        FROM 
                            sale_order so
                        LEFT JOIN 
                            kderp_contract_client kcc ON so.contract_id = kcc.id
                        where so.id in (%s)""" % (quo_ids))
            for id,completion_date_contract in cr.fetchall():
                res[id] = completion_date_contract
        return res
    
    def _get_quotation_from_approved_line(self, cr, uid, ids, context=None):
        res=[]
        for sol in self.pool.get('sale.order.line').browse(cr,uid,ids):
            res.append(sol.order_id.id)
        return res
    
    def _get_quotation_from_contract(self, cr, uid, ids, context=None):
        res=[]
        for kcc in self.pool.get('kderp.contract.client').browse(cr,uid,ids):
            for so in kcc.quotation_ids:
                res.append(so.id)
        return res
    
    _columns={
              
                'currencies':fields.function(_get_quoation_approved_info,method=True,type='many2one',relation='res.currency',size=16,string='Cur.',
                                           multi='_get_quotation_approved_info',
                                           store={
                                                  'sale.order.line':(_get_quotation_from_approved_line,None,35),
                                                  'sale.order':(lambda self, cr, uid, ids, c={}: ids, ['order_line','order_line_m'], 10)
                                                  }),
              
                'total_approved_amount':fields.function(_get_quoation_approved_info,method=True,type='float',digits_compute= dp.get_precision('Product Price'),string='Total',
                                           multi='_get_quotation_approved_info',
                                           store={
                                                  'sale.order.line':(_get_quotation_from_approved_line,None,35),
                                                  'sale.order':(lambda self, cr, uid, ids, c={}: ids, ['order_line','order_line_m'], 10)
                                                  }),
              
                'approved_amount_e':fields.function(_get_quoation_approved_info,method=True,type='float',digits_compute= dp.get_precision('Product Price'),string='Approved E.',
                                           multi='_get_quotation_approved_info',
                                           store={
                                                  'sale.order.line':(_get_quotation_from_approved_line,None,35),
                                                  'sale.order':(lambda self, cr, uid, ids, c={}: ids, ['order_line','order_line_m'], 10)
                                                  }),
                'approved_amount_m':fields.function(_get_quoation_approved_info,method=True,type='float',digits_compute= dp.get_precision('Product Price'),string='Approved M.',
                                           multi='_get_quotation_approved_info',
                                           store={
                                                  'sale.order.line':(_get_quotation_from_approved_line,None,35),
                                                  'sale.order':(lambda self, cr, uid, ids, c={}: ids, ['order_line','order_line_m'], 10)
                                                  }),
                'max_completion_date':fields.function(_get_max_completion,type='date',method=True,string='Max Completion Date'),
                
                'completion_date_contract':fields.function(_get_completion_date_contract,type='date',method=True,string='Comp. Date of Contract',
                                                           store={
                                                                  'sale.order':(lambda self, cr, uid, ids, c={}: ids, ['contract_id'], 10),
                                                                  'kderp.contract.client':(_get_quotation_from_contract, ['completion_date'], 10)
                                                                  }),
                
                'state': fields.selection(STATE_SELECTION, 'Status', readonly=True, select=True),
                'name': fields.char('Code', size=20, required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, select=True),
                'dateofregistration':fields.date('Date of Registration'),
                
                #Client & Address & Information
                'partner_id': fields.many2one('res.partner', 'Client Name', ondelete='restrict', readonly=True, domain="[('customer','=',1)]",states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always'),
                'partner_address_id': fields.many2one('res.partner', 'Client Address', readonly=True,ondelete='restrict', required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
                'partner_invoice_id': fields.many2one('res.partner', 'Invoice Address', readonly=True,ondelete='restrict', required=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
                'completion_date':fields.date('Completion Date'),
                
                'contract_id':fields.many2one('kderp.contract.client','Contract No.',ondelete='restrict'),
                
                #For disable required
                'pricelist_id': fields.many2one('product.pricelist', 'Pricelist'),
                'partner_shipping_id': fields.many2one('res.partner', 'Delivery Address', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Delivery address for current sales order."),
                'invoice_quantity': fields.selection([('order', 'Ordered Quantities')], 'Invoice on', help="The sales order will automatically create the invoice proposition (draft invoice).", readonly=True, states={'draft': [('readonly', False)]}),
                'picking_policy': fields.selection([('direct', 'Deliver each product when available'), ('one', 'Deliver all products at once')],'Shipping Policy', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
                'shop_id': fields.many2one('sale.shop', 'Shop', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
                'order_policy': fields.selection([('manual', 'On Demand')], 'Create Invoice', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
                
                ### Quotation Information ####
                'owner_id': fields.many2one('res.partner', 'Owner Name',ondelete='restrict', domain="[('customer','=',1)]",readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, change_default=True, select=True),
                'location_id': fields.many2one('res.partner', 'Owner Address',ondelete='restrict', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
                
                'project_name':fields.char('Project Name', size=256,select=2),
                                
                'registered_by':fields.many2one('res.users','Registered By',select=2,ondelete='restrict'),#readonly=True,states={'draft': [('readonly', False)]},required=True),
                
                'estimation_e_manager_v':fields.many2one('res.users','Est. E.(V)',ondelete='restrict',select=2),
                'estimation_e_manager_j':fields.many2one('res.users','Est. E.(J)',ondelete='restrict',select=2),
                
                'estimation_m_manager_v':fields.many2one('res.users','Est. M.(V)',ondelete='restrict',select=2),
                'estimation_m_manager_j':fields.many2one('res.users','Est. M.(J)',ondelete='restrict',select=2),
                
                'site_manager_e_id':fields.many2one('res.users','Site Manager(E.)',ondelete='restrict',select=2),
                'site_manager_m_id':fields.many2one('res.users','Site Manager(M.)',ondelete='restrict',select=2),
                'project_manager_id':fields.many2one('res.users', 'Prj. Manager(E.)',ondelete='restrict',select=2),
                'project_manager_m_id':fields.many2one('res.users','Prj. Manager(M.)',ondelete='restrict',select=2),
                
                'description':fields.text('Desc.',select=2),
                'remarks':fields.text('Remarks',select=2),
                
                #Sumbit Information
                'date_order': fields.date('Date of Submit', select=True),
                'quotation_type':fields.selection([('E','Electrical'),('M','Mechanical'),('E/M','Electrical & Mechanical')],'Quotation Type'),
                
                'quotation_submit_line':fields.one2many('kderp.sale.order.submit.line','order_id','Submit detail'),
                
                'order_line': fields.one2many('sale.order.line', 'order_id', 'Breakdown for Electrical',context={'job_type':'E'}, domain=[('job_type','=','E')]),
                'order_line_m':fields.one2many('sale.order.line','order_id','Breakdown for Mechanical',context={'job_type':'M'}, domain=[('job_type','=','M')]),
                
                'summary_quotation_ids':fields.one2many('kderp.summary.of.quotation','order_id','Summary of Quotation',readonly=True), 
               
                #Quotation Attached Info
                'q_attached':fields.function(_get_quotation_attachment,method=True,string='Quotation',readonly=True,type='boolean',multi='quotation_attachment',
                                             store={
                                                    'sale.order':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','q_attached','q_attached_be','q_attached_bm','q_attached_qcombine','q_attached_je','q_attached_jm','q_attached_jcombine'],20)}),
              
                'q_attached_be':fields.function(_get_quotation_attachment,method=True,string='Q.Budget Electrical',readonly=True,type='boolean',multi='quotation_attachment',
                                             store={
                                                    'sale.order':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','q_attached','q_attached_be','q_attached_bm','q_attached_qcombine','q_attached_je','q_attached_jm','q_attached_jcombine'],20)}),
                'q_attached_bm':fields.function(_get_quotation_attachment,method=True,string='Q.Budget Mechanical',readonly=True,type='boolean',multi='quotation_attachment',
                                             store={
                                                    'sale.order':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','q_attached','q_attached_be','q_attached_bm','q_attached_qcombine','q_attached_je','q_attached_jm','q_attached_jcombine'],20)}),
                'q_attached_qcombine':fields.function(_get_quotation_attachment,method=True,string='Q.Budget Combine',readonly=True,type='boolean',multi='quotation_attachment',
                                             store={
                                                    'sale.order':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','q_attached','q_attached_be','q_attached_bm','q_attached_qcombine','q_attached_je','q_attached_jm','q_attached_jcombine'],20)}),
               'q_attached_je':fields.function(_get_quotation_attachment,method=True,string='J.Budget E.',readonly=True,type='boolean',multi='quotation_attachment',
                                             store={
                                                    'sale.order':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','q_attached','q_attached_be','q_attached_bm','q_attached_qcombine','q_attached_je','q_attached_jm','q_attached_jcombine'],20)}),
                'q_attached_jm':fields.function(_get_quotation_attachment,method=True,string='J.Budget M.',readonly=True,type='boolean',multi='quotation_attachment',
                                             store={
                                                    'sale.order':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','q_attached','q_attached_be','q_attached_bm','q_attached_qcombine','q_attached_je','q_attached_jm','q_attached_jcombine'],20)}),
                'q_attached_jcombine':fields.function(_get_quotation_attachment,method=True,string='J.Budget Combine',readonly=True,type='boolean',multi='quotation_attachment',
                                             store={
                                                    'sale.order':(lambda self, cr, uid, ids, c={}: ids, None, 5),
                                                    'ir.attachment':(_get_attachement_link,['res_model','res_id','q_attached','q_attached_be','q_attached_bm','q_attached_qcombine','q_attached_je','q_attached_jm','q_attached_jcombine'],20)}),
               
                'job_e_id':fields.many2one('account.analytic.account', 'Job. (E)',select=1,ondelete='restrict', domain=[('job_type','=','E')]),
                'q_budget_no_e':fields.char('Budget No.',size=20),
                'q_exrate_e':fields.float("Ex.Rate"),
                'q_prj_budget_amount_e':fields.float("W.B. Amount (E)"),
                'budget_state_e':fields.char('Budget Status',size=10),
                'temp_percentage_e':fields.float('%',digits=(16,2)),
                
                'job_m_id':fields.many2one('account.analytic.account', 'Job. (M)',select=1,ondelete='restrict', domain=[('job_type','=','M')]),
                'q_budget_no_m':fields.char('Budget No.',size=20),
                'q_exrate_m':fields.float("Ex.Rate"),
                'q_prj_budget_amount_m':fields.float("W.B. Amount  (M)"),
                'budget_state_m':fields.char('Budget Status',size=10),
                'temp_percentage_m':fields.float('%',digits=(16,2)),
                
                #selection=[('Negotiated','Negotiating'),('Fixed','Fixed')]
                'negotiating':fields.function(_get_negotiating,type='char',size=16,select=1,
                                              method=True,
                                              string='Final Price',
                                              store={
                                                  'sale.order.line':(_get_quotation_from_approved_line,None,35),
                                                  'sale.order':(lambda self, cr, uid, ids, c={}: ids, ['order_line','order_line_m'], 10)
                                                  }),
                
                'total_working_budget':fields.function(_get_quotation_total,method=True,string="W.B. Amt.(M&E)",type='float',
                                                digits=(16,0), store={'sale.order':(lambda self, cr, uid, ids, c={}: ids, None, 20)}),
              
                'sort_state':fields.function(_get_sort_state,method=True,string="Sort",type='integer',
                                            store={'sale.order':(lambda self, cr, uid, ids, c={}: ids, None, 20)}),
              
                 'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Untaxed Amount',
                                                    store={
                                                        'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','order_line_m'], 10),
                                                        'sale.order.line': (_get_quotation_from_approved_line, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                                                    },
                                                    multi='sums', help="The amount without tax.", track_visibility='always'),
                 'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
                                                store={
                                                    'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','order_line_m'], 10),
                                                    'sale.order.line': (_get_quotation_from_approved_line, ['price_unit', 'tax_id', 'discount','product_uom_qty'], 10),
                                                },
                                                multi='sums', help="The tax amount."),
                 'amount_total':fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
                                    store={
                                        'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line','order_line_m'], 10),
                                        'sale.order.line': (_get_quotation_from_approved_line, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
                                    },
                                    multi='sums', help="The total amount."),
                      }
    _sql_constraints = [
                        ('quotation_number_error_mask', "CHECK (name ilike 'QH__-____-%' or name ilike 'QP__-____-%' or name ilike 'QS__-____-%')",  'KDVN Error: The quotation number must like QPYY-XXXX, QSYY-XXXX, QHYY-XXXX !'),
                        ('quotation_number_error_unique',"unique(name)","KDVN Error: The quotation number must be unique !")]
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
        r=self.pool.get('ir.rule').clear_cache(cr,uid)
        new_obj=super(sale_order, self).create(cr, uid, vals, context=context)
        return new_obj
    
    def write(self, cr, uid, ids, vals, context={}):
        
        tmp_ids = ids
        if isinstance(ids,int):
            ids = [ids]
        #Chuyen ids sang dang chuoi (1,2,3,4)
        so_ids = ",".join(map(str,ids))
        
        cr.execute("""
                    Select distinct
                        currency_id,
                        contract_id,
                        job_e_id as job_id,
                        so.state as old_state
                    from 
                        sale_order so left join sale_order_line sol on so.id = sol.order_id
                    where job_type='E' and so.id in (%s)
                    Union
                    Select distinct
                        currency_id,
                        contract_id,
                        job_m_id as job_id,
                        so.state as old_state
                    from 
                        sale_order so left join sale_order_line sol on so.id = sol.order_id
                    where job_type='M' and so.id in (%s)""" % (so_ids,so_ids))
       
        old_values = cr.fetchall() #Lay gia tri contract, job, currency truoc khi duoc ghi vao database
        
        must_update = False
    
        new_state =''
        
        if 'state' in vals:
            new_state = vals['state']
            
        if 'contract_id' in vals:
            must_update = True
            
        if 'job_e_id' in vals:
            must_update = True
            
        if 'job_m_id' in vals:
            must_update = True
        
        if 'order_line' in vals or not vals.get('order_line', False): #Neu co thay doi hoac xoa line
            if not vals.get('order_line', False):
                must_update = True
            else:
                for t1,id,value in vals['order_line']:
                    value = value or {}
                    if 'currency_id' in value:
                        must_update = True
                    if 'price_unit' in value or 'discount' in value:
                        must_update = True
                                
        if 'order_line_m' in vals or not vals.get('order_line_m', False):
            if not vals.get('order_line_m', False):
                must_update = True
            else:
                for t1,id,value in vals['order_line_m']:
                    value = value or {}
                    if 'currency_id' in value:
                        must_update = True
                    if 'price_unit' in value or 'discount' in value:
                        must_update = True
        
        ########### Luu vao database ##########
        new_obj = super(sale_order, self).write(cr, uid, tmp_ids, vals, context=context)
        
        #cr.commit()
        ################
        
        #Kiem tra xem co thay doi trang thai tu done sang khac, hoac tu khac sang done
        #Kiem tra xem cac gia tri contract, job currency cu co cai nao trong khong
        
        list_to_update = [] #Luu nhung contract, job, currency da cap nhat vao danh sach update
        #raise osv.except_osv("E","E %s-%s" % (new_state,old_values))
        old_state1=''
        for old_curr_id,old_contract_id,old_job_id,old_state in old_values:
            old_state1=old_state
            if new_state!='' and (new_state!=old_state and (new_state=='done' or old_state=='done')):
                 must_update = True
            if must_update:
                if old_curr_id and old_contract_id and old_job_id:
                    list_to_update.append([old_curr_id,old_contract_id,old_job_id])
                    
        if must_update:
            for so in self.browse(cr,uid,ids):
                if so.state=='done':
                    for sol in so.order_line:
                        if sol.currency_id and so.contract_id and so.job_e_id:
                            try:
                                list_to_update.index([sol.currency_id.id,so.contract_id.id,so.job_e_id.id])
                            except:
                                list_to_update.append([sol.currency_id.id,so.contract_id.id,so.job_e_id.id])
                    for sol in so.order_line_m:
                        if sol.currency_id and so.contract_id and so.job_m_id:
                            try:
                                list_to_update.index([sol.currency_id.id,so.contract_id.id,so.job_m_id.id])
                            except:
                                list_to_update.append([sol.currency_id.id,so.contract_id.id,so.job_m_id.id])
        
        #raise osv.except_osv("E","%s-%s-%s"  %(list_to_update,old_state1,new_state))
        for curr_id,ctc_id,job_id in list_to_update:
            chk = self.pool.get('kderp.quotation.contract.project.line').check_update_and_create(cr,uid,ctc_id,job_id,curr_id)
        self.pool.get('ir.rule').clear_cache(cr,uid)
        return new_obj
        
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'state':'draft',
            'completion_date':False,
            'date_order':False,
            'contract_id':False, 
            'q_attached':False,
            'q_attached_be':False,
            'q_attached_bm':False,
            'q_attached_qcombine':False,
            'q_attached_je':False,
            'q_attached_jm':False,
            'q_attached_jcombine':False,
            
            'budget_state_e':False,
            'budget_state_m':False,
            'q_budget_no_e':False,
            'q_budget_no_m':False,
            
            'temp_percentage_m':0.0,
            'temp_percentage_e':0.0,
            
            'q_exrate_e':0.0,
            'q_exrate_m':0.0,                                                
                                                
            'q_prj_budget_amount_e':0.0,
            'q_prj_budget_amount_m':0.0,
            
            'total_working_budget':0.0,
            
            'quotation_submit_line':[],
            'order_line':[],
            'order_line_m':[],
            'summary_quotation_ids':[],
            'kderp_quotation_temporary_line':[],
            'kderp_quotation_temporary_line_m':[]       
        })
        #raise osv.except_osv("E",default)
        res=super(sale_order, self).copy(cr, uid, id, default, context)
        self.write(cr, uid, [res], {'date_order':False})
        self.pool.get('ir.rule').clear_cache(cr,uid)
        return res
    
    
    def _get_newcode(self,cr,uid,context={}):
        cr.execute("""Select 
                        prefix ||
                        substring(date_part('year',current_date)::text from 3 for 2) || '-' ||
                        lpad(coalesce(max((substring(so.name from length(prefix)+4 for padding))::int)+1,1)::text,padding,'0') ||
                        '-' || suffix
                    from 
                        ir_sequence cis
                    left join
                        sale_order so on so.name ilike cis.prefix || substring(date_part('year',current_date)::text from 3 for 2) || '-' || lpad('_',padding,'_') || '%%'  
                    where 
                        code ilike 'kderp_' || (Select location_user from res_users where id=%s) ||'_quotation' and
                        active=True
                    group by
                        cis.id""" % uid)
        new_code=False
        res = cr.fetchone()
        if res:
            new_code = res[0]
        return new_code
    
    _defaults={
               'name':_get_newcode,
               'date_order': lambda *x: False,
               }
    _sql_constraints=[('kderp_quotation_code','unique(name)','Code for Quotation must be unique !')]
    
    def onchange_owner_id(self, cr, uid, ids, owner):#Auto fill location when change Owner
        if not owner:
            return {'value':{'location_id':False}}
        return {'value':{'location_id':owner}}
  
    def onchange_partner_id(self, cr, uid, ids, part, context=None): #Auto fill data when change Client
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False, 'partner_address_id': False,  'payment_term': False, 'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context={})
        #if the chosen partner is not a company and has a parent company, use the parent to choose the delivery, the 
        #invoicing addresses and all the fields related to the partner.
        if part.parent_id and not part.is_company:
            part = part.parent_id
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact','default'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid

        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_address_id': addr['default'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
        }
        if pricelist:
            val['pricelist_id'] = pricelist
        return {'value': val}
    
    def action_work_received(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True
    
    def action_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True
    
    def action_cancel_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def action_done_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True
    
    def open_quotation(self, cr, uid, ids, context=None):
        if not context:
            context={}
        context['initial_mode']='edit';
        
        return {
            "type": "ir.actions.act_window",
            "name": "Quotation",
            "res_model": 'sale.order',
            "res_id": ids[0] if ids else False,
            "view_type": "form",
            "view_mode": 'form,tree',
            'context':context,
            "target":"current",
            'nodestroy': True,
            'domain': "[('id','in',%s)]" % ids
        }
        
    def init(self,cr):
        cr.execute("""Update wkf set on_create=False where on_create=True and osv='sale.order';""")
        
sale_order()

class kderp_sale_order_submit_line(Model):
    _name='kderp.sale.order.submit.line'
    _description = 'KDERP Sale Order Submit Line'
    
    def _get_tax_default(self,cr,uid,context):
        tax_ids = self.pool.get('account.tax').search(cr, uid,[('type_tax_use','=','sale'),('active','=',True),('default_tax','=',True)])
        return tax_ids
   
    def _get_amount_line(self, cr, uid, ids, name, args, context={}):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, line.amount, 1)
            
            vat_amount = cur_obj.round(cr, uid,line.currency_id, taxes['total_included']-line.amount)
            total = cur_obj.round(cr, uid,line.currency_id,taxes['total_included'])
            res[line.id]={'tax_amount':vat_amount,
                          'subtotal':total}
        return res
    
    def _get_sale_order(self, cr, uid, ids, context=None):
        result = {}
        for so in self.pool.get('sale.order').browse(cr, uid, ids, context=context):
            for sml in so.quotation_submit_line:
                result[sml.id] = True
        return result.keys()
    
    def _get_approved_line(self, cr, uid, ids, context=None):
        result = {}
        for sol in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            if sol.order_id:
                for sml in sol.order_id.quotation_submit_line:
                    result[sml.id]=True
        return result.keys()
    
    def _get_approved(self, cr, uid, ids, name, args, context={}):
        res={}
        if ids:
            sol_ids=",".join(map(str,ids))
            cr.execute("""Select 
                            ksosl.id,
                            sum(case when 
                                job_type='E' 
                            then 
                                (coalesce(price_unit,0)+coalesce(discount,0)) 
                            else
                                0 end) as approved_amount_e,
                            sum(case when 
                                job_type='M' 
                            then 
                                (coalesce(price_unit,0)+coalesce(discount,0)) 
                            else
                                0 end) as approved_amount_m
                        from 
                            kderp_sale_order_submit_line ksosl
                        left join
                             sale_order_line sol on ksosl.order_id= sol.order_id and ksosl.currency_id = sol.currency_id
                        where
                            ksosl.id in (%s)
                        group by
                            ksosl.id""" % sol_ids)
            for sol in cr.dictfetchall():
                res[sol.pop('id')]=sol
        return res
    
    _columns={
              'currency_id':fields.many2one('res.currency','Cur.',required=True),
              'tax_id': fields.many2many('account.tax', 'kderp_sale_order_submit_tax', 'order_line_id', 'tax_id', 'Tax', domain="[('parent_id','=',False),('type_tax_use','=','sale')]",change_default=True),
              'amount': fields.float('Amount', required=True, digits_compute= dp.get_precision('Product Price')),
              
              'tax_amount':fields.function(_get_amount_line,type='float',string='VAT',method=True,multi='_get_amount_submit_line',digits_compute= dp.get_precision('Product Price'),store=
                                           {'kderp.sale.order.submit.line':(lambda self, cr, uid, ids, c={}: ids, None, 5)}
                                           ),
              'subtotal':fields.function(_get_amount_line,type='float',string='Sub-Total',method=True,multi='_get_amount_submit_line',digits_compute= dp.get_precision('Product Price'),store=
                                           {'kderp.sale.order.submit.line':(lambda self, cr, uid, ids, c={}: ids, None, 5)}
                                           ),
              
              'note':fields.char('Desc.',size=64),
              'order_id':fields.many2one('sale.order','Order',ondelete='restrict'),
              
              #Approved Amount
              'approved_amount_e':fields.function(_get_approved,type='float',string='Approved Amount E',method=True,multi='_get_approved_amount',digits_compute= dp.get_precision('Product Price'),store={
                                                         'kderp.sale.order.submit.line':(lambda self, cr, uid, ids, c={}: ids, ['currency_id','order_id'], 5),
                                                         'sale.order':(_get_sale_order, ['order_line','order_line_m','quotation_submit_line'], 10),
                                                         'sale.order.line':(_get_approved_line, None, 15)}),
              'approved_amount_m':fields.function(_get_approved,type='float',string='Approved Amount M',method=True,multi='_get_approved_amount',digits_compute= dp.get_precision('Product Price'),
                                                  store={
                                                         'kderp.sale.order.submit.line':(lambda self, cr, uid, ids, c={}: ids, ['currency_id','order_id'], 5),
                                                         'sale.order':(_get_sale_order, ['order_line','order_line_m','quotation_submit_line'], 10),
                                                         'sale.order.line':(_get_approved_line, None, 15)}),
              }
    _sql_constraints=[('kderp_quotation_submit_currency','unique(currency_id,order_id)','Currency for Submit Detail must be unique !')]
    
    _defaults={
               'amount':0.0,
               'tax_id':_get_tax_default
               }
kderp_sale_order_submit_line()

class sale_order_line(Model):
    _name = 'sale.order.line'
    _description = 'Detail of Breakdown Quotation'
    _inherit = 'sale.order.line'

    def _get_job_type(self,cr,uid,context={}):
        if not context:
            context={}
        return context.get('job_type',False)
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit + (line.discount or 0.0)
            res[line.id] = price 
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        cr.execute("Update sale_order_line set state='draft' where id in (%s)" % ",".join(map(str,ids)))
        return super(sale_order_line, self).unlink(cr, uid, ids, context=context)
    
    _columns = {
                'name':fields.char('Description',size=250),
                'currency_id':fields.many2one('res.currency','Cur.',required=True),
                'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price')),
                'discount':fields.float('Discount',required=True),
                'expected_amount':fields.float("Expected",states={'cancel': [('readonly', True)]}),
                'job_type':fields.selection([('E','Electrical'),('M','Mechanical')],'Type',required=True),                
                'order_id': fields.many2one('sale.order', 'Quotation', required=True, ondelete='restrict', select=True),
                'price_subtotal': fields.function(_amount_line, string='Subtotal'),
                #Remove attr required
                'delay': fields.float('Delivery Lead Time',readonly=True, states={'draft': [('readonly', False)]}),
                'product_uom': fields.many2one('product.uom', 'Unit of Measure ', readonly=True, states={'draft': [('readonly', False)]}),
                'product_uom_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), readonly=True, states={'draft': [('readonly', False)]}),
                'state': fields.selection([('cancel', 'Cancelled'),('draft', 'Draft'),('confirmed', 'Confirmed'),('exception', 'Exception'),('done', 'Done')], 'Status',readonly=True),
                'type': fields.selection([('make_to_stock', 'from stock'), ('make_to_order', 'on order')], 'Procurement Method', readonly=True, states={'draft': [('readonly', False)]}),
                }
    _sql_constraints=[('kderp_breakdown_currency','unique(currency_id,order_id,job_type)','Currency for Approved Detail must be unique !')]
    _order = 'order_id desc, sequence'
    _defaults = {
                 'job_type':_get_job_type,
                 #'amount':0.0,
                 'discount':0.0,
                 'state':'draft',
                 'expected_amount':0.0
                 }
sale_order_line()

class kderp_summary_of_quotation(Model):
    _name = 'kderp.summary.of.quotation'
    _description = 'KDERP Summary Of Quotation'
    _auto = False
    _columns={
              'currency_id':fields.many2one('res.currency','Cur.'),
              'amount':fields.float('Sub-Total'),
              'order_id':fields.many2one('sale.order','Order')
              }
    def init(self,cr):
        cr.execute("""Create or replace view kderp_summary_of_quotation as
                      Select 
                            row_number() over (order by order_id,currency_id) as id,
                            sol.order_id,
                            currency_id,
                            sum(price_unit+discount) as amount
                      from 
                          sale_order_line sol 
                      group by
                          order_id,currency_id""")
kderp_summary_of_quotation()