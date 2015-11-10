insert into instruments (
symbol, 
instrument_desc, 
sector_desc, 
industry_desc, 
country_desc, 
market_cap, 
pe_ratio, 
last_price, 
last_change, 
last_volume, 
div_yield, 
return_on_assets, 
return_on_equity, 
return_on_investment, 
current_ratio, 
quick_ratio, 
lt_debt_to_equity, 
total_debt_to_equity, 
gross_margin, 
operating_margin, 
profit_margin, 
earnings_date
) 
select 
o.symbol, 
max(o.instrument_desc), 
max(o.sector_desc), 
max(o.industry_desc), 
max(o.country_desc), 
max(o.market_cap), 
max(o.pe_ratio), 
max(o.last_price), 
max(o.last_change), 
max(o.last_volume), 
max(f.div_yield), 
max(f.return_on_assets), 
max(f.return_on_equity), 
max(f.return_on_investment), 
max(f.current_ratio), 
max(f.quick_ratio), 
max(f.lt_debt_to_equity), 
max(f.total_debt_to_equity), 
max(f.gross_margin), 
max(f.operating_margin), 
max(f.profit_margin), 
max(f.earnings_date) 
from 
stg_instruments_overview o left outer join stg_instruments_financial f on o.symbol = f.symbol 
group by o.symbol