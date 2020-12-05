select column_name, data_type
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE table_name = %s;