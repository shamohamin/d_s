copy(select st.stock_name, 
        dsi.profit as daily_profit,
        dsi.min_price as day_min_price,
        dsi.max_price as day_max_price,
        dsi.final_price as day_final_price,
        dsi.date_of_profit as "date",
        dsi.number_of_buyers as "buyers_in_day",
        dsi.volume_of_buy as "volumn_of_buy_in_day",
        scps.persons_num_of_buyers,
        scps.company_num_of_buyers,
        scps.persons_amount_of_buy,
        scps.company_amount_of_buy,
        scps.persons_num_of_seller,
        scps.company_num_of_seller,
        scps.persons_amount_of_sells,
        scps.company_amount_of_sells
  from stocks st
    join daily_stocks_info dsi
    on st.stock_id = dsi.stock_id
    join stocks_comapny_person_summary scps
    on scps.stock_id = st.stock_id)
to "/Users/mohamd/Documents/bors/src/database.csv"
with (format csv, header on);