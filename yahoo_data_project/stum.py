#------------------------------------------------------------------------------
#   Author:     Claus Herther, Calogica
#   Date:       12/26/2013
#   Comments:   downloads Yahoo Finance data for each batch
#               gets daily data as well as historic data (if specified)
#
#------------------------------------------------------------------------------

#import sys, os
import time, datetime, string
import extracter
import loader

def main(ex_instr, ld_instr, ex_hist, ld_hist):

	print "ld_hist", ld_hist
	print bool(ld_hist) == True
	current_date = time.strftime("%Y%m%d")
	week_day = datetime.datetime.today().weekday()
	history_start_date = datetime.datetime.today()-datetime.timedelta(days=3) #weeks=53*25)

	errors = {'symbol':'error_message'}

	print "#---------------------------------------------------------"
	print "Date: ", current_date
	print "Start Date: ", history_start_date
	print "#---------------------------------------------------------"

	##############################################################################
	config = extracter.get_config()

	fv = config['finviz']
	yh = config['yahoo']
	
	if (ex_instr == 1):
		extracter.extract_instruments(fv)

	if (ld_instr == 1):
		loader.load_instruments(fv)

	if (ex_hist == 1):
		instruments = loader.get_instruments("")
		print "Downloading " + str(len(instruments)) + " symbols" 
		extracter.extract_data_yahoo_instruments(yh, instruments, history_start_date)  

	if (ld_hist == 1):

		instruments = loader.get_instruments("")
		print "Loading history for " + str(len(instruments)) + " symbols" 
		loader.load_history_data(config, instruments)
		loader.process_metrics()


	##############################################################################

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:            # argv[0] is the script name 
        print sys.argv[4]
        main(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]))
    else:
        main(1, 1, 1, 1)
    sys.exit(0)
