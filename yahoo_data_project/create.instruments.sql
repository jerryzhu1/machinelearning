drop table instruments;

create table instruments
(
	instrument_id serial,
	symbol varchar(10),
	instrument_desc varchar(300),
	sector_desc varchar(300),
	industry_desc varchar(300),
	country_desc varchar(100),
	market_cap decimal(18,4),
	pe_ratio decimal(18,4),
	last_price decimal(18,4),
	last_change decimal(18,4),
	last_volume int,
	div_yield decimal(18,4),
	return_on_assets decimal(18,4),
	return_on_equity decimal(18,4),
	return_on_investment decimal(18,4),
	current_ratio decimal(18,4),
	quick_ratio decimal(18,4),
	lt_debt_to_equity decimal(18,4),
	total_debt_to_equity decimal(18,4),
	gross_margin decimal(18,4),
	operating_margin decimal(18,4),
	profit_margin decimal(18,4),
	earnings_date date,
	primary key (instrument_id)
);
create index nx_instruments_symbol on instruments (symbol);

-----------------------------------------------------------
-- Overview
-----------------------------------------------------------
drop table stg_instruments_overview;

create table stg_instruments_overview
(
	symbol varchar(10),
	instrument_desc varchar(300),
	sector_desc varchar(300),
	industry_desc varchar(300),
	country_desc varchar(100),
	market_cap decimal(18,4),
	pe_ratio decimal(18,4),
	last_price decimal(18,4),
	last_change decimal(18,4),
	last_volume int,
	batch varchar(50)
);

drop table import_instruments_overview;

create table import_instruments_overview
(
	batch_id varchar(100),
	symbol varchar(100),
	instrument_desc varchar(300),
	sector_desc varchar(300),
	industry_desc varchar(300),
	country_desc varchar(100),
	market_cap varchar(100),
	pe_ratio varchar(100),
	last_price varchar(100),
	last_change varchar(100),
	last_volume varchar(100)
);

-----------------------------------------------------------
-- Financial
-----------------------------------------------------------
drop table stg_instruments_financial;

create table stg_instruments_financial
(	
	symbol varchar(10),
	market_cap decimal(18,4),
	div_yield decimal(18,4),
	return_on_assets decimal(18,4),
	return_on_equity decimal(18,4),
	return_on_investment decimal(18,4),
	current_ratio decimal(18,4),
	quick_ratio decimal(18,4),
	lt_debt_to_equity decimal(18,4),
	total_debt_to_equity decimal(18,4),
	gross_margin decimal(18,4),
	operating_margin decimal(18,4),
	profit_margin decimal(18,4),
	earnings_date date,
	last_price decimal(18,4),
	last_change decimal(18,4),
	last_volume decimal(18,4),
	batch varchar(50)
);

drop table import_instruments_financial;

create table import_instruments_financial
(	
	batch_id varchar(100),
	symbol varchar(100),
	market_cap varchar(100),
	div_yield varchar(100),
	return_on_assets varchar(100),
	return_on_equity varchar(100),
	return_on_investment varchar(100),
	current_ratio varchar(100),
	quick_ratio varchar(100),
	lt_debt_to_equity varchar(100),
	total_debt_to_equity varchar(100),
	gross_margin varchar(100),
	operating_margin varchar(100),
	profit_margin varchar(100),
	earnings_date varchar(100),
	last_price varchar(100),
	last_change varchar(100),
	last_volume varchar(100)
);

--insert into instruments (symbol, instrument_desc, sector_desc, industry_desc, country_desc, market_cap, pe_ratio, last_price, last_change, last_volume, batch) select symbol, instrument_desc, sector_desc, industry_desc, country_desc, cast(market_cap as decimal(18,4)), cast(pe_ratio as decimal(18,4)), cast(last_price as decimal(18,4)), cast(replace(last_change, '%','') as decimal(18,4))/100, cast(last_volume as int), 'test' from import_instruments