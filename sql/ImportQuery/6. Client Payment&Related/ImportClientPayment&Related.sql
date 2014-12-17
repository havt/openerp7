﻿
-- ######################## KDERP Invoice
--Select * from kderp_invoice
-- Insert into kderp_invoice 
-- 	(id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	amount_tax,
-- 	name,
-- 	currency_id,
-- 	date,
-- 	subtotal,
-- 	tax_percent,
-- 	total_amount,
-- 	notes)
-- Select
-- 	kri.id,
-- 	kri.create_uid,
-- 	kri.create_date,
-- 	kri.write_date,
-- 	kri.write_uid,
-- 	amount_tax,
-- 	invoice_no,
-- 	rc.id,
-- 	kri.date,
-- 	subtotal,
-- 	tax_percent,
-- 	total_amount,
-- 	notes
-- from dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select 
-- 		kri.id,
-- 		kri.create_uid,
-- 		kri.create_date,
-- 		kri.write_date,
-- 		kri.write_uid,
-- 		amount_tax,
-- 		kri.name as invoice_no,
-- 		rc.name as currency,
-- 		kri.date,
-- 		subtotal,
-- 		tax_percent,
-- 		total_amount,
-- 		notes
-- 	from 
-- 		kdvn_red_invoice kri
-- 	left join
-- 		res_currency rc on currency_id = rc.id') 
-- as kri(	
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	amount_tax numeric,
-- 	invoice_no varchar(32),
-- 	currency varchar(3),
-- 	date date,
-- 	subtotal numeric,
-- 	tax_percent numeric,
-- 	total_amount numeric,
-- 	notes varchar(32))
-- left join
-- 	res_currency rc on currency=rc.name;

-- Select max(id) from kderp_invoice  --1239
-- alter SEQUENCE kderp_invoice_id_seq RESTART with 1240


-- ######################## KDERP Client Payment
-- alter table account_invoice ADD column curr_state varchar(16)
-- 
Select * from account_invoice 
-- Insert into account_invoice
-- 	(
-- 	id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	number,
-- 	date_invoice,
-- 	contract_id,
-- 	partner_id,
-- 	owner_id,
-- 	address_id,
-- 	invoice_address_id,
-- 	payment_term_id,
-- 	attached_progress_sent,
-- 	attached_progress_received,
-- 	name,
-- 	comment,
-- 	currency_id,
-- 	curr_state,
-- 	state,
-- 	exrate,
-- 	account_id,
-- 	journal_id,
-- 	company_id,
-- 	reference_type,
-- 	tax_base
-- 	)
-- Select
-- 	kpfc.id,
-- 	kpfc.create_uid,
-- 	kpfc.create_date,
-- 	kpfc.write_date,
-- 	kpfc.write_uid,
-- 	number,
-- 	kpfc.date,
-- 	contract_id,
-- 	client_id,
-- 	owner_id,
-- 	rpa.id as address_id,
-- 	rpai.id as invoice_address_id,
-- 	payment_term_line_id,
-- 	attached_progress_sent,
-- 	attached_progress_received,
-- 	itemofrequest,
-- 	remark,
-- 	rc.id as currency_id,
-- 	state as curr_state,
-- 	'cancel' as state,
-- 	claim_exrate,
-- 	21 as account_id,
-- 	2 as journal_id,
-- 	1 as company_id,
-- 	'none' as reference_type,
-- 	'p' as tax_base
-- from dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select 
-- 		kpfc.id,
-- 		kpfc.create_uid,
-- 		kpfc.create_date,
-- 		kpfc.write_date,
-- 		kpfc.write_uid,
-- 		number,
-- 		kpfc.date,
-- 		kpfc.contract_id,
-- 		client_id,
-- 		owner_id,
-- 		address_id,
-- 		invoice_address_id,
-- 		payment_term_line_id,
-- 		attached_progress_sent,
-- 		attached_progress_received,
-- 		itemofrequest,
-- 		description as remark,
-- 		state,
-- 		pc.name as curr_name,
-- 		case when pc.name=''VND'' then 1 else coalesce(kr.rate,pc.rate) end as claim_exrate
-- 	from
-- 		kdvn_payment_from_client kpfc
-- 	left join
-- 		kdvn_received kr on kpfc.id=payment_id
-- 	left join
-- 		project_currency pc on contract_currency_id=pc.id') 
-- as kpfc(
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	number varchar(16),
-- 	date date,
-- 	contract_id int,
-- 	client_id int,
-- 	owner_id int,
-- 	address_id int,
-- 	invoice_address_id int,
-- 	payment_term_line_id int,
-- 	attached_progress_sent boolean,
-- 	attached_progress_received boolean,
-- 	itemofrequest varchar(256),
-- 	remark varchar(256),
-- 	state varchar(16),
-- 	curr_name varchar(3),
-- 	claim_exrate numeric)
-- left join
-- 	res_currency rc on curr_name=rc.name
-- left join
-- 	res_partner rpa on kpfc.address_id=rpa.address_id
-- left join
-- 	res_partner rpai on invoice_address_id = rpai.address_id

-- Select * from account_account where code ilike '131%' --21
-- Update account_invoice set type='out_invoice'
-- Select max(id) from account_invoice --1564
-- alter SEQUENCE account_invoice_id_seq RESTART with 1649


-- IMPORT PAYMENT LINE - ACCOUNT INVOICE LINE
-- alter SEQUENCE account_invoice_line_id_seq RESTART with 1
-- 157: "511100"
-- 
-- Insert into account_invoice_line
-- 	(invoice_id,
-- 	account_analytic_id,
-- 	amount,
-- 	advanced,
-- 	retention,
-- 	account_id,
-- 	quantity,
-- 	name)
-- Select
-- 	invoice_id,
-- 	account_analytic_id,
-- 	ail.amount,
-- 	ail.advanced,
-- 	ail.retention,
-- 	157 as account_id,
-- 	1 as quantity,
-- 	aaa.code || '-' || aaa.name
-- from dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select 
-- 		kpfc.id as invoice_id,
-- 		job_id as account_analytic_id,
-- 		case when project_type=''E'' then amount_e else amount_m end as amount,
-- 		adv_payment*job_per as advanced,
-- 		retention*job_per as retention	
-- 	from 
-- 		kdvn_payment_from_client kpfc
-- 	left join
-- 		(Select
-- 			kpcr.contract_id,
-- 			kp.id as job_id,
-- 			project_type,
-- 			case when (coalesce(contract_amount_e,0)+coalesce(contract_amount_m,0))<>0 then contract_amount_e/(coalesce(contract_amount_e,0)+coalesce(contract_amount_m,0)) else 0 end as job_per
-- 		from
-- 			kdvn_project_contract_rel kpcr
-- 		left join
-- 			kdvn_project kp on project_id=kp.id
-- 		left join
-- 			kdvn_contract_client kcc on kpcr.contract_id=kcc.id
-- 		where
-- 			kp.project_type=''E''
-- 		Union
-- 		Select
-- 			kpcr.contract_id,
-- 			kp.id as job_id,
-- 			project_type,
-- 			case when  (coalesce(contract_amount_e,0)+coalesce(contract_amount_m,0))<>0 then contract_amount_m/(coalesce(contract_amount_e,0)+coalesce(contract_amount_m,0)) else 0 end as job_per
-- 		from
-- 			kdvn_project_contract_rel kpcr
-- 		left join
-- 			kdvn_project kp on project_id=kp.id
-- 		left join
-- 			kdvn_contract_client kcc on kpcr.contract_id=kcc.id
-- 		where
-- 			kp.project_type=''M'') kcpr on kpfc.contract_id = kcpr.contract_id')
-- as AIL(	
-- 	invoice_id int,
-- 	account_analytic_id int,
-- 	amount numeric,
-- 	advanced numeric,
-- 	retention numeric)
-- left join
-- 	account_analytic_account aaa on account_analytic_id=aaa.id
-- left join
-- 	account_invoice ai on invoice_id=ai.id
-- where coalesce(account_analytic_id,0)>0

-- ###################TAX SUBMIT

--Import Tax

-- Insert into account_invoice_line_tax 
-- 	(invoice_line_id,tax_id) 
-- Select 
-- 	ail.id as invoice_line_id,
-- 	at.id as tax_id
-- from dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select 
-- 		id,
-- 		coalesce(taxes_percent,0)
-- 	from 
-- 		kdvn_payment_from_client
-- 	where
-- 		coalesce(taxes_percent,0)>0')
-- as ail_old(	
-- 	payment_id int,
-- 	per numeric)
-- left join
-- 	account_tax at on type='percent' and per/100.0-at.amount=0 and type_tax_use='sale'
-- left join
-- 	account_invoice_line ail on payment_id=ail.invoice_id
-- where coalesce(ail.id,0)>0

-- IMPORT PAYMENT VAT INOVICE

-- ######################## KDERP Invoice
--Select * from kderp_invoice

-- Insert into 
-- 	kderp_payment_vat_invoice
-- 	(id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	payment_id,
-- 	amount,
-- 	vat_invoice_id,
-- 	note)
-- Select
-- 	id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	payment_id as ai_id,
-- 	amount,
-- 	vat_invoice_id,
-- 	note
-- from dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select 
-- 		id,
-- 		create_uid,
-- 		create_date,
-- 		write_date,
-- 		write_uid,
-- 		payment_id as ai_id,
-- 		amount,
-- 		vat_invoice_id,
-- 		note
-- 	from 
-- 		kdvn_payment_vat_invoice') 
-- as kri(	
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	payment_id int,
-- 	amount numeric,
-- 	vat_invoice_id int,
-- 	note varchar(8))

-- Select max(id) from kderp_payment_vat_invoice  --1283
-- alter SEQUENCE kderp_payment_vat_invoice_id_seq RESTART with 1284


-- ######################## KDERP Received
-- Journal ID=9 "Bank";9 (VND)
-- insert into kderp_received
-- 	(id,
-- 	create_uid,
-- 	create_date,
-- 	write_date,
-- 	write_uid,
-- 	client_payment_id,
-- 	date,
-- 	amount,
-- 	currency_id,
-- 	exrate,
-- 	journal_id)
-- Select
-- 	kr.id,
-- 	kr.create_uid,
-- 	kr.create_date,
-- 	kr.write_date,
-- 	kr.write_uid,
-- 	payment_id as client_payment_id,
-- 	kr.date,
-- 	recv_amount as amount,
-- 	rc.id as currency_id,
-- 	rate as exrate,
-- 	9 as journal_id
-- from dblink('dbname=KDVN_Data user=openerp password=!@#Admin1120 host=172.16.10.192',
-- 	'Select 
-- 		id,
-- 		create_uid,
-- 		create_date,
-- 		write_date,
-- 		write_uid,
-- 		payment_id,
-- 		date,
-- 		coalesce(actual_amount,0)+coalesce(actual_tax_amount,0) as recv_amount,
-- 		''VND'' as recv_cur,
-- 		rate
-- 	from 
-- 		kdvn_received
-- 	where
-- 		coalesce(payment_id,0)>0') 
-- as kr(	
-- 	id int,
-- 	create_uid int,
-- 	create_date date,
-- 	write_date date,
-- 	write_uid int,
-- 	payment_id int,
-- 	date date,
-- 	recv_amount numeric,
-- 	recv_cur varchar(3),
-- 	rate numeric)
-- left join
-- 	res_currency rc on kr.recv_cur=rc.name

-- Select max(id) from kderp_received  --1281
-- alter SEQUENCE kderp_received_id_seq RESTART with 1282