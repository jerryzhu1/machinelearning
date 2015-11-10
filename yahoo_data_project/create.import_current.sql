drop table instruments;
create table import_current
(
  symbol character varying(10),
  instrument_desc character varying(300),
  last_date date,
  last_time character varying(100),
  price_open character varying(100),
  price_hi character varying(100),
  price_lo character varying(100),
  price_close character varying(100),
  volume character varying(100),
  book_value character varying(100),
  ex_div_date character varying(100)
)
;