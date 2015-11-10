drop table instruments_portfolio;
create table instruments_portfolio as
(
select cast('TF Diversified' as varchar(100)) as portfolio, symbol from instruments
where symbol in ('SPY',	'QQQ',	'IWM',	'EWC',	'EWJ',	'EWU',	'EWG',	'EWD',	'ENOR',	'EWQ',	
'EWP',	'EWI',	'EWL',	'EWO',	'EIS',	'EEM',	'FXI',	'EWH',	'EWT',	'EWS',	'EWY',	'EWA',	
'ENZL',	'EWW',	'EWZ',	'EZA',	'PIN',	'THD',	'EPHE',	'EWM',	'TUR',	'RSX',	'RUSS',	'GREK',	'FM',	
'AFK',	'NGE',	'TLT',	'IEF',	'IEI',	'SHY',	'MBB',	'BNDX',	'BUND',	'FXY',	'FXE',	'ULE',	'EUO',	'FXB',	'FXF',	'FXC',	'FXA',	'USO',	'UNG',	'UHN',	'UGA',	'GLD',	'GLL',	'SLV',	'ZSL',	'JJC',	'PPLT',	'PALL',	'BOM',	'BAL',	'NIB',	'JO',	'CANE',	'WEAT',	'CORN',	'SOYB',	'COW',	'DBA',	'MOO',	'WOOD',	'VNQ')
) primary key (portfolio, symbol) 
;
drop table history_ma;
create table history_ma 
(
	symbol varchar(10),
	last_date date,
	price_close decimal(18,2),
	hi55d decimal(18,2),
	lo20d decimal(18,2),
	ma10 decimal(18,4),
	ma20 decimal(18,4),
	ma50 decimal(18,4),
	ma100 decimal(18,4),
	ma150 decimal(18,4),
	ma200 decimal(18,4),
	primary key (symbol, last_date)
)
;

drop materialized view history_portfolio;
create materialized view history_portfolio
as
(
	select 
	    h.symbol, 
	    h.last_date, 
	    h.price_open,
	    h.price_hi,
	    h.price_lo,	   
	    h.price_close,
	    lag(h.price_close,1) over(partition by h.symbol order by h.last_date) as close_yst,
	    lag(h.price_close,(52*5/12)) over(partition by h.symbol order by h.last_date) as close_01mo,
	    lag(h.price_close,(52*5/4)) over(partition by h.symbol order by h.last_date) as close_03mo,
	    lag(h.price_close,(52*5/2)) over(partition by h.symbol order by h.last_date) as close_06mo,
	    lag(h.price_close,(52*5)) over(partition by h.symbol order by h.last_date) as close_12mo,
	    max(cast(h.price_close as decimal(18,2))) over(partition by h.symbol order by h.last_date rows between 55 preceding and 1 preceding) as hi55d,
	    min(cast(h.price_close as decimal(18,2))) over(partition by h.symbol order by h.last_date rows between 20 preceding and 1 preceding) as lo20d,
	    avg(cast(h.price_close as decimal(18,2))) over(partition by h.symbol order by h.last_date rows 10-1 preceding) as ma10,
	    avg(cast(h.price_close as decimal(18,2))) over(partition by h.symbol order by h.last_date rows 20-1 preceding) as ma20,
	    avg(cast(h.price_close as decimal(18,2))) over(partition by h.symbol order by h.last_date rows 50-1 preceding) as ma50,
	    avg(cast(h.price_close as decimal(18,2))) over(partition by h.symbol order by h.last_date rows 100-1 preceding) as ma100,
	    avg(cast(h.price_close as decimal(18,2))) over(partition by h.symbol order by h.last_date rows 150-1 preceding) as ma150,
	    avg(cast(h.price_close as decimal(18,2))) over(partition by h.symbol order by h.last_date rows 200-1 preceding) as ma200,
	    -- true range
		greatest(
			-- high - low
		    h.price_hi-h.price_lo,
		    -- high - prior close
			abs(h.price_hi-lag(h.price_close,1) over(partition by h.symbol order by h.last_date)),
		    -- low - prior close
		    abs(h.price_lo-lag(h.price_close,1) over(partition by h.symbol order by h.last_date))
			) as true_range
	from 
		history h
		inner join
		(select distinct symbol from instruments_portfolio) i on h.symbol = i.symbol
	where
	    h.last_date >= (current_date-(365*5))
) with data;
;

create materialized view history_portfolio_metrics
as
(select 
	    h.*,
	    avg(cast(h.true_range as decimal(18,2))) over(partition by h.symbol order by h.last_date rows 20-1 preceding) as atr20,
	    avg(cast(h.true_range as decimal(18,2))) over(partition by h.symbol order by h.last_date rows 100-1 preceding) as atr100,
	    (h.price_close/h.close_yst  -1) as roc_01d,
	    (h.price_close/h.close_01mo -1) as roc_01mo,
	    (h.price_close/h.close_03mo -1) as roc_03mo,
	    (h.price_close/h.close_06mo -1) as roc_06mo,
	    (h.price_close/h.close_12mo -1) as roc_12mo
	from
		history_portfolio h		
) with data;

-- Metrics TF
select
	ip.portfolio,
	h.symbol,
	i.instrument_desc,
	ip.asset_class,
	ip.market,
	h.last_date,
	h.price_close,
	cast(h.atr100 as decimal(18,2)) as atr100,
	cast(h.atr100/h.price_close*100 as decimal(18,4)) as atr100_perc,
	cast(h.hi55d as decimal(18,2)) as hi55d,
	cast(h.lo20d as decimal(18,2)) as lo20d,
	cast(h.ma10 as decimal(18,2)) as ma10,
	cast(h.ma50 as decimal(18,2)) as ma50,
	cast(h.ma100 as decimal(18,2)) as ma100,
	cast(h.ma200 as decimal(18,2)) as ma200
from 
	history_portfolio_metrics h
	inner join
	instruments i
		on h.symbol = i.symbol
	inner join
	instruments_portfolio ip on h.symbol = ip.symbol
where 
	portfolio = 'TF Diversified'
	and
	h.last_date = 
	(select max(last_date) from history_ma)
	and
	(price_close > ma50)
	and
	(price_close > ma100)
	and
	(price_close > ma200)
	and
	(ma10 > ma100)
	and
	(ma50 > ma200)
	--and
	--(price_close > hi55d)
order by asset_class, market, symbol;

-- Metrics Ivy20
select
	ip.portfolio,
	h.symbol,
	i.instrument_desc,
	ip.asset_class,
	ip.market,
	h.last_date,
	h.price_close,
	cast(h.atr100 as decimal(18,2)) as atr100,
	cast(h.atr100/h.price_close*100 as decimal(18,4)) as atr100_perc,
	cast(h.ma200 as decimal(18,2)) as ma200,
	cast(h.roc_01mo as decimal(18,2)) as roc_01mo,
	cast(h.roc_03mo as decimal(18,2)) as roc_03mo,
	cast(h.roc_06mo as decimal(18,2)) as roc_06mo,
	cast(h.roc_12mo as decimal(18,2)) as roc_12mo,
	cast((h.roc_01mo + h.roc_03mo)/2 as decimal(18,2)) as roc_01_03mo_avg,
	cast((h.roc_03mo + h.roc_06mo + h.roc_12mo)/3 as decimal(18,2)) as roc_03_12mo_avg
from 
	history_portfolio_metrics h
	inner join
	instruments i
		on h.symbol = i.symbol
	inner join
	instruments_portfolio ip on h.symbol = ip.symbol
where 
	portfolio = 'Ivy20'
	and
	h.last_date = 
	(select max(last_date) from history_ma)
	and
	(price_close > ma200)
order by asset_class, market, symbol;


-- 12 month returns

 