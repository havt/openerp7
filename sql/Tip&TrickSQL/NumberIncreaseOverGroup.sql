'Tạm Ứng / Advance Payment Cash No.' || row_number() over (PARTITION BY kap.user_id,extract(ISOYEAR FROM date_received_money) order by kap.user_id,payment_voucher_no asc) as Description