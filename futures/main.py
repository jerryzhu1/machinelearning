from common import g2json as gd
import Quandl as q
import pandas as pd
from datetime import date 
from datetime import timedelta
import logging
import optparse
import sys
import getopt
import MySQLdb


FORMAT = '%(asctime)-15s %(levelname)s %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# filename='out.log', filemode='w',
# logger.basicConfig(format=FORMAT, level=logging.DEBUG)
# logger = log.getLogger('tcpserver')
def get_db():

	return MySQLdb.connect("localhost","root","","calogica")

def get_symbols_source():
    """
    -----------------------------------------------------------------------
        look up symbols from Google Doc
    -----------------------------------------------------------------------
    """
    key = "1Vbgw4yw1crruuH05aDSHXBvD_Bb_Tq47Fs04MNJVDk4"
    sheet = "Symbols"

    symbols = pd.read_json(gd.get_gdoc(key, sheet, return_json=True))

    return symbols

def get_symbols(symbol):
    """
    -----------------------------------------------------------------------
        get symbols from db
    -----------------------------------------------------------------------
    """
    table_name = "symbols"
    sql = 'select * from {0}'.format(table_name)
    if symbol:
    	sql = sql + ' where symbol="{0}"'.format(symbol)
    print sql

    db = get_db()
    tbl = pd.read_sql(sql, con=db)
    db.close()

    return tbl

def get_price_data_source(symbols, start_date):

    """ 
    -----------------------------------------------------------------------
        gets Quandl data for each symbol
    ----------------------------------------------------------------------- 
    """ 

    data = None
    for i, row in symbols.iterrows():

        month = "1"
        search = "{0}/{1}_{2}{3}".format(row.database, row.source, row.symbol, month)

        frequency = "daily"

        logger.info('requesting {0} data for {1} from {2} on from quandl'.format(frequency, row.symbol, start_date))	

        df = q.get(search, authtoken="xkXtzxzRcDyizWAV9r3_", 
                   collapse=frequency,
                   sort_order="asc", 
                   trim_start=start_date)

        # print 'data from quandl', df.columns

        df['Symbol'] = row.symbol
        df['Code'] = row.code
        if 'Open Interest' in df.columns:
            df=df.rename(columns = {'Open Interest':'OI'})
        else:
        	df['OI'] = 0
        
        if 'Prev. Day Open Interest' in df.columns:
            df=df.rename(columns = {'Prev. Day Open Interest':'Prev_OI'})
        else:
        	df['Prev_OI'] = 0

        
        df.columns = [x.lower().replace(' ', '_') for x in df.columns]
        
        if (data is not None):        
            data = data.append(df, ignore_index=False)
            logger.info('appending {0} {1}, {2} rows ({3})'.format(row.contractname, df.symbol[0], len(df.index), len(data.index)))
        else:
            # first time around?
            data = df
            logger.info('initializing {0} {1}, {2} rows ({3})'.format(row.contractname, df.symbol[0], len(df.index), len(data.index)))     

    return data    


def trunc_data(data, table_name, key, index):

    groups = data.groupby(key)

    db = get_db()
    c = db.cursor()

    for name, group in groups:

		logger.info('truncating {0}'.format(name))

		index_start = group.index.min().date()
		del_cmd = "delete from {0} where {1} ='{2}' and {3} >= '{4}'".format(table_name, key, name, index, index_start)
		logger.info(del_cmd)

		c.execute(del_cmd)
		db.commit()
        
    c.close()
    db.close()

def save_data(data, table_name, index, append=False):

    db = get_db()

    if db:
        if append:
            data.to_sql(con=db, name=table_name, index=index, if_exists='append', flavor='mysql')

        else:

            data.to_sql(con=db, name=table_name, index=index, if_exists='replace', flavor='mysql')

        # magically all the dataz are in there
        tbl = pd.read_sql('select * from {0};'.format(table_name), con=db)

        db.close()

    return tbl

def check_dupes(table_name, key):

	db = get_db()

	df = pd.read_sql('select {0}, count(*) from {1} group by {0} having count(*) > 1;'.format(key, table_name), con=db)

	db.close()
	# len(df[df.duplicated(subset=key)== True])

	logger.warning('Found {0} dupes'.format(len(df)))

	if len(df):
		print df 

def update_symbols():

	symbols_source = get_symbols(None)
	symbols = save_data(symbols_source, "symbols", index=False, append=False)

	return symbols

def update_prices(symbols, days):

	""" 
	-----------------------------------------------------------------------
		update_data
	----------------------------------------------------------------------- 
	""" 

	d = date.today() - timedelta(days=days)
	start_date = d.strftime('%Y-%m-%d')
	logger.info(start_date)

	prices = get_price_data_source(symbols, start_date)

	logger.info('downloaded {0} rows'.format(len(prices.index)))

	# TODO: change col names to lower case and remove spaces
	table_name = "prices"
	key="code"
	index="date"

	groups = prices.groupby(key)

	for name, group in groups:

		logger.info('processing {0}'.format(name))
		trunc_data(group, table_name, key, index)
		save_data(group, table_name, index=True, append=True)
		logger.info('saved {0} rows to mysql for {1}'.format(len(group.index), name))

	# check_dupes('prices', 'Date, Code')
def main():

	""" 
	-----------------------------------------------------------------------
		main
	----------------------------------------------------------------------- 
	""" 

	parser = optparse.OptionParser()

	parser.add_option('-s',
	                  '--symbol',
	                  help='Optional: specify symbol to update, otherwise update all')

	parser.add_option('-p',
	                  '--prices',
	                  default='True',
	                  help='Optional: set to False to skip updating price data')
	
	parser.add_option('-d',
	                  '--days',
	                  default=10,
	                  help='Optional: number of past days to use for price data updates, default is 10 days')


	(options, args) = parser.parse_args()

	symbol = options.symbol
	price_data = False if options.prices == False or options.prices == 'False' else True
	days = int(options.days)

	days = days/5.0*7
	logger.info(days)

	if not symbol:
		logger.info('updating symbols')
		symbols = update_symbols()
	else:
		symbols = get_symbols(symbol)

	if price_data:
		prices = update_prices(symbols, days)

if __name__ == "__main__":
    main()


