#------------------------------------------------------------------------------
#   Author:     Claus Herther, Calogica
#   Date:       12/26/2013
#   Comments:   downloads Yahoo Finance data for each batch
#               gets daily data as well as historic data (if specified)
#
#------------------------------------------------------------------------------

import sys, os
import shutil
from subprocess import call
import time, datetime, string
import psycopg2
#import mysql.connector
#from mysql.connector import errorcode
import glob
import databaser as db

con = None
f = None
cur = None

data_dir = '/home/ubuntu/data/'


#------------------------------------------------------------------------------
def load_data(file_pattern, delete_command, insert_command):
#------------------------------------------------------------------------------

    try:
        # get latest file for the pattern
        file_name = max(glob.iglob(file_pattern), key=os.path.getctime)
        print file_name
    
        with db.db_get_connection() as con:
        
            cur = con.cursor()
            if (delete_command):
                print delete_command
                cur.execute(delete_command)
            
                print "Truncated"

            with open(file_name, 'r') as f:
            
                lines = f.read().splitlines()    
            
                for line in lines:
            
                    data = line.split(",")
                    print data[0]
                    if (data[0] != "Date" and data[0] != '"No."'):
            
                        print insert_command
                        print data
    #                    cur.mogrify(insert_command, data)
                        cur.execute(insert_command, data)
    
                        con.commit()
        
        
    except psycopg2.DatabaseError, e:   
    #except mysql.connector.Error, e:
    
        if con:
            con.rollback()
    
        print 'Error %s' % e    
        sys.exit(1)

    except IOError, e:    

        if con:
            con.rollback()

        print 'Error %s' % e   
        sys.exit(1)
    except:
        err_msg = "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "ERROR:", err_msg 
        
    finally:
    
        if con:
            con.close()

        if f:
            f.close()
  

#------------------------------------------------------------------------------
def copy_data(file_name, target_table, truncate):
#------------------------------------------------------------------------------

    try:

        if (truncate):
            
            con = db.db_get_connection()
            cur = con.cursor()
            cmd_truncate = "truncate table {0}".format(target_table)
            print cmd_truncate
            cur.execute(cmd_truncate)
            con.commit()
            
            con.close()

            print "Truncated"

        
        db.copy_file_to_table(file_name, target_table)
    
            
    except psycopg2.DatabaseError, e:   
    #except mysql.connector.Error, e:
    
        if con:
            con.rollback()
    
        print 'Error %s' % e    
        sys.exit(1)

    except:
        err_msg = "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "ERROR:", err_msg 
    finally:
    
        if con:
            con.close()
            print "Closing db connection..."

#------------------------------------------------------------------------------
def transform_data(delete_command, insert_command):
#------------------------------------------------------------------------------
    
    
    try:

        con = db.db_get_connection()
        cur = con.cursor()
        if (delete_command):
            print delete_command
            cur.execute(delete_command)
        
            print "Deleted"


        if (insert_command):
            print insert_command
            cur.execute(insert_command)
            con.commit()
    
            print "Inserted"
                
    except psycopg2.DatabaseError, e:   
    #except mysql.connector.Error, e:
    
        if con:
            con.rollback()
    
        print 'Error %s' % e    
        sys.exit(1)


    except:
        err_msg = "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "ERROR:", err_msg 
        
    finally:
    
        if con:
            con.close()
            print "Closing db connection..."
            
  
#------------------------------------------------------------------------------
def load_instruments(config):
#------------------------------------------------------------------------------

    batches = config['batches']
    for i,b in enumerate(batches):

        print "Importing current data for:", b

        file_pattern = data_dir + '/current/import_instruments_' + b + '*'
        print file_pattern
        file_name = max(glob.iglob(file_pattern), key=os.path.getctime)
        
        stg_delete_command = "delete from stg_instruments_{0} where batch = '{0}'".format(b)
        stg_insert_command = "insert into stg_instruments_{0} (symbol, {1}, batch)".format(b, batches[b]['fields'])
        stg_insert_command += " select symbol, {0}, '{1}' from import_instruments_{1} i ".format(batches[b]['query'],b)

        # truncate import table before the 1st batch
        truncate = True #(i==0)
        
        #print stg_insert_command
        try:
            print 'importing'
        
            # copy file data
            copy_data(file_name, 'import_instruments_{0}'.format(b), truncate)
            # stage each batch
            print stg_insert_command
            transform_data(stg_delete_command, stg_insert_command)
             
        except:
            err_msg = "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
            print "ERROR:", err_msg     

    # dedupe batches (symbols can be in multiple file) and load to final table
    load_delete_command = "delete from instruments where symbol in (select distinct symbol from stg_instruments_overview)"
    load_insert_command = "insert into instruments (symbol, {0}, {1}) ".format(batches['overview']['fields'], batches['financial']['fields']) 
    load_insert_command += "select o.symbol, {0}, {1} ".format(batches['overview']['transform'], batches['financial']['transform']) 
    load_insert_command += "from stg_instruments_overview o left outer join stg_instruments_financial f on o.symbol = f.symbol "
    load_insert_command += "group by o.symbol"

    try:
        print 'loading...'
    
        transform_data(load_delete_command, load_insert_command)
             
    except:
        err_msg = "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "ERROR:", err_msg     
            
            
#------------------------------------------------------------------------------
def load_history_data(config, instruments):
#------------------------------------------------------------------------------

    for i in instruments:
        s = i[0]

        print "Importing historic data for:", s

        file_name = data_dir + '/history/history_' + s + '.csv'
        #import_file = data_dir + '/history/import_history.csv'
        
        if os.path.isfile(file_name):
        
            print file_name
            #shutil.copyfile(file_name, import_file)

            # copy file data
            copy_data(file_name, 'import_history', True)
    
            delete_command = "delete from history where symbol = '" + s + "' and last_date in (select distinct last_date from import_history)"
            insert_command = "insert into history (symbol, last_date, price_open, price_hi, price_lo, price_close, volume, adj_close) "
            insert_command += "select '" + s + "', last_date, price_open, price_hi, price_lo, price_close, volume, adj_close from import_history"
    
        
            try:
                transform_data(delete_command, insert_command)        
            except:
                err_msg = "Unexpected error:", sys.exc_info()[0]
                print "ERROR:", err_msg 

# REFRESH MATERIALIZED VIEW

#------------------------------------------------------------------------------
def process_metrics():
#------------------------------------------------------------------------------

    cmd_1 = "REFRESH MATERIALIZED VIEW history_portfolio"
    cmd_2 = "REFRESH MATERIALIZED VIEW history_portfolio_metrics"
    try:
        transform_data("", cmd_1)        
        transform_data("", cmd_2)        
    except:
        err_msg = "Unexpected error:", sys.exc_info()[0]
        print "ERROR:", err_msg 

#------------------------------------------------------------------------------
def get_instruments(start_symbol):
#------------------------------------------------------------------------------

    cmd = "SELECT DISTINCT symbol FROM instruments"
    if (len(start_symbol)>0):
        cmd += " WHERE instrument_id > (SELECT instrument_id from instruments WHERE symbol='{0}')".format(start_symbol)
        
    cmd += " ORDER BY symbol"
    
    print cmd
    dt = db.db_get_data(cmd)
    return dt

        
