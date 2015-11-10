#------------------------------------------------------------------------------
#   Author:     Claus Herther, Calogica
#   Date:       12/26/2013
#   Comments:   downloads Yahoo Finance data for each batch
#               gets daily data as well as historic data (if specified)
#
#------------------------------------------------------------------------------

import sys, os
import urllib
import urllib2
import time, datetime, string
import json
import databaser as db

current_date = time.strftime("%Y%m%d")
week_day = datetime.datetime.today().weekday()

errors = {'symbol':'error_message'}
script_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = '/home/ubuntu/data/'

#---------------------------------------------------------
def get_config():
#---------------------------------------------------------
    with (open(script_dir + '/config.json','r')) as f:
    
        j = json.loads(f.read())
    
        f.close()
    
    return j


#---------------------------------------------------------
def get_batches(name):
#---------------------------------------------------------
    return get_config[name]

#---------------------------------------------------------
def extract_url(url, file_name, step):
#---------------------------------------------------------
    # open url and save locally to file
    try:
        u = urllib2.urlopen(url)
        f = open(file_name, 'w')

        print "Saving file:", file_name
        f.write(u.read())

        f.close()
    except urllib2.HTTPError:
        
        err_msg = "URL was not found:", url
        print "ERROR:", err_msg 
        errors[step] = err_msg 

    except:
        err_msg = "Unexpected error:", sys.exc_info()[0]
        #print "Retrying:", err_msg 
        errors[step] = err_msg 
        #raise
        #try:
        #    download_url(url, file_name, b)
        #except:
        #err_msg = "Failed retrying: Unexpected error:", sys.exc_info()[0]
        print "ERROR:", err_msg 
        #    errors[step] = err_msg   
            
def check_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

#---------------------------------------------------------
def extract_data_yahoo_historic(config, history_start_date):
#---------------------------------------------------------
    
    url_history = config['url_history']
    history_dir = data_dir + 'history/'   
    
    date_param = '&a={0}&b={1}&c={2}'.format(history_start_date.month-1, history_start_date.day, history_start_date.year)
    print date_param
    
    batches = config['batches']
    
    for i,b in enumerate(batches):
    
        print "---------------------------------------------------------"
        print "Processing batch:", b
        print "---------------------------------------------------------"
    
        encoded_args = urllib.urlencode(batches[b])
 
        print 'Encoded: ', encoded_args
 
      # historic data
        symbols = string.split(batches[b]['s'], '+')
        
        for j, s in enumerate(symbols):
            
            #print j, s

            url = url_history + s 
            url = url + date_param + '&g=d&ignore=.csv'

            print "Processing historic data for:", s, 'from', url

            # file name for current batch and today's date
            check_dir(history_dir)
                
            #file_name = history_dir + 'history_' + s + '_' + current_date + '.csv'
            file_name = history_dir + 'history_' + s + '.csv'
        
            extract_url(url, file_name, s)
        
    if (len(errors)>1):
        print ""
        print "---------------------------------------------------------"
        print "Encountered the following errors:"
        for i, e in enumerate(errors):
            if (e != 'symbol'):
                print e, errors[e]
        print "---------------------------------------------------------"
#---------------------------------------------------------
def extract_data_yahoo_instruments(config, instruments, history_start_date):
#---------------------------------------------------------
    
    url_history = config['url_history']
    history_dir = data_dir + 'history/'   
    
    date_param = '&a={0}&b={1}&c={2}'.format(history_start_date.month-1, history_start_date.day, history_start_date.year)
    #print date_param
    
    for i in instruments:
        s = i[0]
        print s

        url = url_history + s 
        url = url + date_param + '&g=d&ignore=.csv'

        print "Processing historic data for:", s, 'from', url

        # file name for current batch and today's date
        check_dir(history_dir)
            
        #file_name = history_dir + 'history_' + s + '_' + current_date + '.csv'
        file_name = history_dir + 'history_' + s + '.csv'
    
        extract_url(url, file_name, s)
        
    if (len(errors)>1):
        print ""
        print "---------------------------------------------------------"
        print "Encountered the following errors:"
        for i, e in enumerate(errors):
            if (e != 'symbol'):
                print e, errors[e]
        print "---------------------------------------------------------"
           
#---------------------------------------------------------
def extract_data_yahoo_batches(config, extract_current, extract_history):
#---------------------------------------------------------
    url_current = config['url_current']
    url_history = config['url_history']
    current_dir = data_dir + current_date
    history_dir = data_dir + 'history/'   
    
    batches = config['batches']
    
    for i,b in enumerate(batches):
    
        print "---------------------------------------------------------"
        print "Processing batch:", b
        print "---------------------------------------------------------"
    
        encoded_args = urllib.urlencode(batches[b])
 
        print 'Encoded: ', encoded_args
 
        if (extract_current):
            url = url_current + encoded_args
            print 'Downloading from', url

            # file name for current batch and today's date
            check_dir(current_dir)
                    
            file_name = current_dir + '/current_' + b + '_' + current_date + '.csv'

            extract_url(url, file_name, b)
        
            
        if (extract_history):
            # historic data
            symbols = string.split(batches[b]['s'], '+')
            
            for j, s in enumerate(symbols):
                
                #print j, s

                url = url_history + s 
                url = url + '&a=00&b=00&c=2012&g=d&ignore=.csv'
                print "Processing historic data for:", s, 'from', url

                # file name for current batch and today's date
                check_dir(history_dir)
                    
                #file_name = history_dir + 'history_' + s + '_' + current_date + '.csv'
                file_name = history_dir + 'history_' + s + '.csv'
            
                extract_url(url, file_name, s)
        
    if (len(errors)>1):
        print ""
        print "---------------------------------------------------------"
        print "Encountered the following errors:"
        for i, e in enumerate(errors):
            if (e != 'symbol'):
                print e, errors[e]
        print "---------------------------------------------------------"

#---------------------------------------------------------
def extract_instruments(config):
#---------------------------------------------------------

    config_url = config['url']
    batches = config['batches']
    
    for i,b in enumerate(batches):
    
        print "---------------------------------------------------------"
        print "Processing batch:", b
        print "---------------------------------------------------------"

        batch_id = batches[b]['id']
        url = config_url + batch_id
        
        print 'Downloading from', url

        # file name for current batch and today's date
        
        current_dir = data_dir + 'current'
        check_dir(current_dir)
                    
        file_name = current_dir + '/import_instruments_' + b + '.csv'

        extract_url(url, file_name, b)
                        
    if (len(errors)>1):
        print ""
        print "---------------------------------------------------------"
        print "Encountered the following errors:"
        for i, e in enumerate(errors):
            if (e != 'symbol'):
                print e, errors[e]
        print "---------------------------------------------------------"


    return batches
