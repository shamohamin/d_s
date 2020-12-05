DROP TABLE IF EXISTS stocks_comapny_person_summary;
DROP TABLE IF EXISTS daily_stocks_info;
-- DROP TABLE IF EXISTS stocks;

CREATE TABLE IF NOT EXISTS stocks (
    stock_id bigserial PRIMARY KEY,
    url text NOT NULL,
    stock_name varchar(100) NOT NULL
);

ALTER TABLE stocks ALTER COLUMN url SET DATA TYPE varchar(300);
-- Alter TABLE stocks ADD COLUMN trade_url varchar(300) NOT NULL;
ALTER TABLE stocks ALTER COLUMN trade_url DROP NOT NULL;

CREATE TABLE IF NOT EXISTS stocks_comapny_person_summary (
    stocks_comapny_person_summary_id bigserial PRIMARY KEY,
    persons_num_of_buyers bigint NOT NULL,
    company_num_of_buyers bigint NOT NULL,
    persons_amount_of_buy varchar(100) NOT NULL,
    company_amount_of_buy varchar(100) NOT NULL,
    persons_num_of_seller bigint NOT NULL,
    company_num_of_seller bigint NOT NULL,
    persons_amount_of_sells varchar(100) NOT NULL,
    company_amount_of_sells varchar(100) NOT NULL,
    stock_id bigint REFERENCES stocks(stock_id) ON DELETE CASCADE NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_stocks_info (
    id bigserial PRIMARY KEY,
    stock_id bigint REFERENCES stocks(stock_id) ON DELETE CASCADE NOT NULL,
    profit numeric(6, 2) NOT NULL,
    min_price numeric(10, 2) NOT NULL,
    max_price numeric(10, 2) NOT NULL,
    final_price numeric(10, 2) NOT NULL,
    date_of_profit varchar(100) NOT NULL,
    number_of_buyers numeric(10, 0) NOT NULL,
    volume_of_buy varchar(100) NOT NULL 
);

-- ALTER TABLE daily_stocks_info ADD COLUMN number_of_buyers numeric(10, 0) NOT NULL;
-- ALTER TABLE daily_stocks_info ADD COLUMN volume_of_buy varchar(100) NOT NULL;