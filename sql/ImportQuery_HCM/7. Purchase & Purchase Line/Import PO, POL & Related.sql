﻿
-- XU LY LAI THUE CO TRUONG HOP TINH THEO ADVANCE HOAC CHI CO THUE KO CO AMOUNT (TRUONG HOP THUE NHAP KHAU)
-- IMPORT TAX PHAI LINK VAO RES_MODEL, RES_ID
-- #IMPORT CURRENCY
-- alter SEQUENCE res_currency_rate_id_seq RESTART 1
-- Insert into res_currency_rate
-- 	(create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	currency_id,
-- 	rate,
-- 	name)
-- Select 
-- 	kpc.create_uid,
-- 	kpc.create_date,
-- 	kpc.write_date,
-- 	kpc.write_uid,
-- 	rc.id as currency_id,
-- 	rate,
-- 	kpc.name as date
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		kpcr.create_uid,
-- 		kpcr.create_date,
-- 		kpcr.write_date,
-- 		kpcr.write_uid,
-- 		kpc.name as curr_name,
-- 		rate,
-- 		kpcr.name as date
-- 	from 
-- 		kdvn_purchase_currency_rate kpcr
-- 	left join
-- 		kdvn_purchase_currency kpc on kpcr.kdvn_purchase_currency_id=kpc.id
-- 	where 
-- 		coalesce(kdvn_purchase_currency_id,0)>0') 
-- as kpc(	
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	curr_name varchar(3),
-- 	rate numeric,
-- 	name date)
-- left join
-- 	res_currency rc on curr_name=rc.name
-- where coalesce(rc.id,0)>0

-- Delete SELECT * from account_tax where description='HM13-0003-M008'

-- ###########IMPORT PURCHASE
-- ## IMPORT TAX
-- select max(id) from account_tax ;
-- alter table purchase_order drop column amount_tax --Please check before delete
-- ALTER SEQUENCE account_tax_id_seq RESTART 1849
-- BASE CODE Taxeable: 20, Deducte Amount Received Tax: 21
-- Tax 133100 23 (Co the sua thanh thue nhap khau)
-- Insert into account_tax 
--   	(company_id,sequence,account_collected_id,account_paid_id,base_code_id,ref_base_code_id,tax_code_id,ref_tax_code_id,type,type_tax_use,applicable_type,active,name,description,amount,res_id,res_model)
-- Select
-- 	1,1,23,23,20,20,21,21,'fixed','purchase',true,true,'For ' || po_number,po_number,amount,res_id,'purchase.order' as res_model
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		po.name as po_number,
-- 		tax_amount as amount,
-- 		po.id as res_id
-- 	from 
-- 		purchase_order po
-- 	left join
-- 		purchase_typeoforder pt on typeoforder=pt.id
-- 	left join 
-- 		kdvn_purchase_currency kpc on po.currency_id=kpc.id
-- 	where
-- 		pt.code<>''e'' and
-- 		(
-- 			(
-- 				((kpc.name=''VND'' and round((tax_per*amount_total2/100.0)::numeric,0)<>tax_amount) or kpc.name<>''VND'') 
-- 			and
-- 				case when coalesce(amount_total2,0)=0 then 0 else tax_amount/amount_total2 end not in (0,0.1,0.05)
-- 			)
-- 
-- 		or 
-- 			(coalesce(amount_Total2,0)=0 and coalesce(tax_amount)<>0)
-- 		)')
-- as po_tax(
-- 	po_number varchar(64),
-- 	amount numeric,
-- 	res_id int
-- 	)

-- alter table purchase_order add column curr_state varchar(32)
-- 
-- name,
-- date_order,
-- taxes_id,
-- tax_baseline,
-- ,
-- curr_state,
-- typeoforder,
-- 
-- 'account_analytic_id'
-- 
-- 'address_id':
-- '' --'User in charge'
-- '' --'Manager'
-- 'incoterm_id'
-- 'country_of_origin'
-- 
-- 'pricelist_id'
-- currency_id
-- 'origin
-- 'notes'
-- 
-- 'special_case
-- 'without_contract
-- 
-- 'quotation_attached
-- 'roa_comaprison_attached
-- 'contract_attached'       
-- 'effective_date'
-- 'delivery_date
-- 'cts_date_of_contract'
-- 'cts_date_of_submittin
-- 'cts_date_of_scanned
-- 'cts_date_of_sending
-- 'cts_date_of_receiving
--case when coalesce(amount_total2,0)=0 then 0 else round(tax_amount::numeric/amount_total2::numeric,2) end as per,

-- PURCHASE ORDER
-- 
-- insert into purchase_order
-- 	(
-- 	id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	account_analytic_id,
-- 	name,
-- 	created_uid,
-- 	manager_user_id,
-- 	typeoforder,
-- 	origin,
-- 	date_order ,
-- 	effective_date,
-- 	special_case,
-- 	without_contract,
-- 	partner_id,
-- 	address_id,
-- 	notes,
-- 	quotation_attached ,
-- 	roa_comaprison_attached ,
-- 	contract_attached ,
-- 	delivery_date,
-- 	incoterm_id ,
-- 	country_of_origin ,
-- 	pricelist_id, 
-- 	discount_amount,
-- 	curr_state,
-- 	cts_date_of_contract,
-- 	cts_date_of_submitting,
-- 	cts_date_of_scanned,
-- 	cts_date_of_sending,
-- 	cts_date_of_receiving,
-- 	company_id,
-- 	state
-- 	)
-- Select
-- 	po.id,
-- 	po.create_uid,
-- 	po.create_date,
-- 	po.write_date,
-- 	po.write_uid,
-- 	po.project_id as account_analytic_id,
-- 	po.name,
-- 	po.user_id,
-- 	user_purchase,
-- 	typeoforder,
-- 	origin,
-- 	date_order ,
-- 	effective_date,
-- 	special_case,
-- 	without_contract,
-- 	partner_id,
-- 	rpa.id as partner_address_id,
-- 	notes,
-- 	quotation_attached ,
-- 	roa_comaprison_attached ,
-- 	contract_attached ,
-- 	delivery_date,
-- 	incoterm_id ,
-- 	country_of_origin ,
-- 	pp.id as pricelist_id, 
-- 	discount,
-- 	state as curr_state,
-- 	cts_date_of_contract,
-- 	cts_date_of_submitting,
-- 	cts_date_of_scanned,
-- 	cts_date_of_sending,
-- 	cts_date_of_receiving,
-- 	1 as company_id,
-- 	'cancel' as state
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		po.id,
-- 		po.create_uid,
-- 		po.create_date,
-- 		po.write_date,
-- 		po.write_uid,
-- 		po.project_id,
-- 		po.name,
-- 		po.user_id,
-- 		po.user_purchase,
-- 		case when pt.id=4 then ''ms'' else pt.code end as typeofpurchase,
-- 		po.origin,
-- 		po.date_order,
-- 		effective_date,
-- 		special_case,
-- 		without_contract,
-- 		partner_id,
-- 		partner_address_id,
-- 		notes,
-- 		quotation_attached,
-- 		roa_comaprison_attached,
-- 		contract_attached,
-- 		delivery_date,
-- 		incoterm_id,
-- 		country_of_origin,
-- 		kpc.name as curr_name,
-- 		discount,
-- 		case 
-- 			when state=''final_quotation'' then ''waiting_for_roa''
-- 			when state=''roa_completed'' then ''waiting_for_delivery''
-- 			when state=''delivered'' then ''waiting_for_payment''
-- 		else state end as state,
-- 		cts_date_of_contract,
-- 		cts_date_of_submitting,
-- 		cts_date_of_scanned,
-- 		cts_date_of_sending,
-- 		cts_date_of_receiving
-- 	from 
-- 		purchase_order po 
-- 	left join
-- 		purchase_typeoforder pt on typeoforder=pt.id
-- 	left join
-- 		kdvn_purchase_currency kpc on currency_id=kpc.id
-- 	where pt.code<>''e''')
-- as po(
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	project_id int,
-- 	name varchar(64),
-- 	user_id int,
-- 	user_purchase int,
-- 	typeoforder varchar(2),
-- 	origin varchar(64),
-- 	date_order date,
-- 	effective_date date,
-- 	special_case boolean,
-- 	without_contract boolean,
-- 	partner_id int,
-- 	partner_address_id int,
-- 	notes varchar(512),
-- 	quotation_attached boolean,
-- 	roa_comaprison_attached boolean,
-- 	contract_attached boolean,
-- 	delivery_date date,
-- 	incoterm_id int,
-- 	country_of_origin int,
-- 	curr_name varchar(3), 
-- 	discount numeric,
-- 	state varchar(32),
-- 	cts_date_of_contract date,
-- 	cts_date_of_submitting date,
-- 	cts_date_of_scanned date,
-- 	cts_date_of_sending date,
-- 	cts_date_of_receiving date)
-- left join
-- 	res_partner rpa on partner_address_id=rpa.address_id
-- left join
-- 	product_pricelist pp on curr_name=pp.name and pp.type='purchase';

-- Select max(id) from purchase_order --15306
-- alter SEQUENCE purchase_order_id_seq RESTART with 15307

-- IMPORT PURCHASE TAX
-- 
-- Insert into purchase_order_taxes
-- 	(
-- 	order_id,
-- 	tax_id
-- 	)
-- Select
-- 	po.id as order_id,
-- 	at.id
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		po.id,
-- 		po.name,
-- 		case when coalesce(amount_total2,0)=0 then 0 else tax_amount/amount_total2 end as tax_per,
-- 		case when round((tax_per*amount_total2/100.0)::numeric,case when Kpc.name=''VND'' THEN 0 ELSE 2 END)=tax_amount then tax_per/100.0 else 0 end as tax_per_round
-- 	from 
-- 		purchase_order po 
-- 	left join
-- 		kdvn_purchase_currency kpc on po.currency_id=kpc.id
-- 	left join
-- 		purchase_typeoforder pt on typeoforder=pt.id
-- 	where pt.code<>''e'' and coalesce(tax_amount,0)<>0')
-- as po(
-- 	id int,
-- 	name varchar(64),
-- 	tax_per numeric,
-- 	tax_per_rounded numeric)
-- left join
-- 	account_tax at on 
-- 	((tax_per=at.amount or (res_id=po.id and res_model='purchase.order')) and type_tax_use='purchase') or (tax_per_rounded=at.amount and at.amount>0 and type_tax_use='purchase')
-- where coalesce(at.id,0)>0 and coalesce(at.amount,0)>0;

-- Select count(*) from purchase_order left join purchase_typeoforder pt on typeoforder=pt.id where pt.code<>'e' and  coalesce(tax_amount,0)<>0
-- 


-- -- ---- ################################## 
-- Update product_uom pu
-- set 
-- 	name=exp.name
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select id,name from product_uom ')
-- as exp(
-- 	id int,
-- 	name varchar(64)
-- 	)
-- where pu.id=exp.id
-- -- --select id,name from product_uom,
--  ##################### Product UOM KIEM TRA TRUNG ID
-- Insert into
-- 	product_uom
-- 	(id,name,category_id,rounding,factor,uom_type
-- 	)
-- Select *,'reference'
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select id,name,case when category_id in (12,15) then 1 else case when category_id =13 then 5 else case when category_id>=16 then 1 else category_id end end end,rounding,factor 
-- 	from product_uom
-- 	')
-- as poum(id int,
-- 	name varchar(64),
-- 	category_id int,
-- 	rouding numeric,
-- 	factor numeric)
-- where id not in (Select id from product_uom) 
-- Select max(id) from product_uom_categ--29
-- alter SEQUENCE product_uom_id_seq RESTART with 21
-- alter SEQUENCE product_uom_categ_id_seq RESTART with 15

--insert into product_uom_categ  (id,name) values (14,'square')
-- 
-- Insert into purchase_order_line
-- 	(
-- 	id,
-- 	sequence,
-- 	order_id ,
-- 	product_id ,
-- 	account_analytic_id,
-- 	product_uom ,
-- 	brand_name ,
-- 	name ,
-- 	plan_qty ,
-- 	product_qty ,
-- 	price_unit,
-- 	state)
-- Select
-- 	*,
-- 	'draft'
-- from dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	'Select 
-- 		pol.id,
-- 		pol.sequence,
-- 		order_id,
-- 		product_id,
-- 		pol.project_id,
-- 		product_uom,
-- 		brand_name,
-- 		pol.name,
-- 		case when coalesce(product_qty,0)=0 then coalesce(plan_qty,0) else product_qty end as plan_qty,
-- 		case when coalesce(product_qty,0)=0 then coalesce(plan_qty,0) else product_qty end as product_qty,
-- 		price_unit
-- 	from 
-- 		purchase_order_line pol
-- 	left join
-- 		purchase_order po on order_id = po.id
-- 	left join
-- 		purchase_typeoforder pt on typeoforder=pt.id
-- 	where pt.code<>''e'' and coalesce(pol.project_id,0)>0')
-- as pol(
-- 	id int,
-- 	sequence int,
-- 	order_id int,
-- 	product_id int,
-- 	project_id int,
-- 	product_uom int,
-- 	brand_name int,
-- 	name varchar(256),
-- 	plan_qty numeric,
-- 	product_qty numeric,
-- 	price_unit numeric)
-- Select max(id) from purchase_order_line --38158
-- alter SEQUENCE purchase_order_line_id_seq RESTART with 38159


-- # Stock Picking

-- Insert into stock_picking
-- 	(id,
-- 	origin,
-- 	name,
-- 	move_type,
-- 	auto_picking,
-- 	invoice_state,
-- 	note,
-- 	state,
-- 	purchase_id,
-- 	received_date,
-- 	type,
-- 	company_id)
-- 	
-- Select 
-- 	*,
-- 	1 as company
-- from
-- dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 	' 
-- 	Select 
-- 		st.id,
-- 		st.origin,
-- 		st.name,
-- 		move_type,
-- 		auto_picking,
-- 		invoice_state,
-- 		note,
-- 		st.state,
-- 		purchase_id,
-- 		received_date,
-- 		type
-- 	from
-- 		stock_picking st
-- 	left join
-- 		purchase_order po on purchase_id = po.id
-- 	where 
-- 		coalesce(special_case,False)
-- 	')
-- as st_p(id int,
-- 	origin varchar(64),
-- 	name varchar(64),
-- 	move_type varchar(16),
-- 	auto_picking boolean,
-- 	invoice_state varchar(16),
-- 	note varchar(128),
-- 	state varchar(16),
-- 	purchase_id int,
-- 	received_date date,
-- 	type varchar(16))

-- Select max(id) from stock_picking --489
-- alter SEQUENCE stock_picking_id_seq RESTART with 490


-- # Stock Picking
-- 
-- Insert into stock_move
-- 	(id,
-- 	product_uom,
-- 	product_qty,
-- 	product_id,
-- 	purchase_line_id,
-- 	date_expected,
-- 	date,
-- 	company_id)
-- Select 
-- 	*,
-- 	1 as company_id
-- from
-- 	dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.11',
-- 		'	
-- 		Select 
-- 			id,
-- 			product_uom,
-- 			product_qty,
-- 			product_id,
-- 			purchase_line_id,
-- 			date_planned,
-- 			date
-- 		from 
-- 			stock_move sm
-- 		where
-- 			picking_id in (
-- 					Select 
-- 							st.id
-- 					from
-- 						stock_picking st
-- 					left join
-- 						purchase_order po on purchase_id = po.id
-- 					where 
-- 						coalesce(special_case,False))')
-- as st_p(id int,
-- 	product_uom int,
-- 	product_qty numeric,
-- 	product_id int,
-- 	purchase_line_id int,
-- 	date_expected date,
-- 	date date)

-- Select max(id) from stock_move --1560
-- alter SEQUENCE stock_move_id_seq RESTART with 1561
-- 
Insert into kderp_po_payment_term_line
	(
	create_uid,
	create_date,
	write_date,
	write_uid,	
	order_id,
	type,
	name,
	value_amount,
	sequence,
	due_date)
Select
	create_uid,
	create_date,
	write_date,
	write_uid,	
	order_id,
	type,
	name,
	value_amount,
	sequence,
	due_date
from
	dblink('dbname=KDVN_Data_HCM user=openerp password=admin host=192.168.1.12',
		'	
		Select 
			* 
		from 
			kdvn_po_payment_term_line 
		where 
			coalesce(order_id,0)>0')
as po_term(
	id int,
	create_uid int,
	create_date date,
	write_date date,
	write_uid int,	
	order_id int,
	type varchar(16),
	name varchar(128),
	value_amount numeric,
	sequence int,
	due_date date)
where po_term.order_id not in (Select order_id from kderp_po_payment_term_line) and po_term.order_id in (Select id from purchase_order)
--  and id not in (select id from kderp_po_payment_term_line)
-- Select max(id) from kderp_po_payment_term_line --13029
-- -- alter SEQUENCE kderp_po_payment_term_line_id_seq RESTART with 13030

