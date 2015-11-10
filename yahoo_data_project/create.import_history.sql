drop table history;
create table history
(
	symbol varchar(10),
	last_date date,
	price_open decimal(18,4),
	price_hi decimal(18,4),
	price_lo decimal(18,4),
	price_close decimal(18,4),
	volume decimal(18,4),
	adj_close decimal(18,4),
primary key (symbol, last_date)
);

-- 	Date,Open,High,Low,Close,Volume,Adj Close

create table import_history
(
	last_date date,
	price_open decimal(18,4),
	price_hi decimal(18,4),
	price_lo decimal(18,4),
	price_close decimal(18,4),
	volume decimal(18,4),
	adj_close decimal(18,4)
);