#------------------------------------------------------------------------------
#   Author:     Claus Herther, Calogica
#   Date:       3/16/2014
#   Comments:   common database functions
#------------------------------------------------------------------------------

import sys, os
from subprocess import call
import time, datetime, string
import psycopg2
import glob

con = None
f = None
cur = None


#------------------------------------------------------------------------------
def db_get_connection():
#------------------------------------------------------------------------------
    print "Getting db connection..."
    con = psycopg2.connect(host='trend.cclfxblbv7ec.us-west-2.rds.amazonaws.com',database='trend', user='calogica',password='calogica') 
    return con

#------------------------------------------------------------------------------
def db_get_connection_command():
#------------------------------------------------------------------------------
    return "psql -h\"trend.cclfxblbv7ec.us-west-2.rds.amazonaws.com\" -d\"trend\" -U\"calogica\""
    
#------------------------------------------------------------------------------
def db_get_data(command):
#------------------------------------------------------------------------------

    try:

        con = db_get_connection()
        cur = con.cursor()
        print "Executing db command..."
        cur.execute(command)
        rows = cur.fetchall()
        con.commit()
        
        return rows
        
    except psycopg2.DatabaseError, e:    
    
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
        err_msg = "Unexpected error:", sys.exc_info()[0]
        print "ERROR:", err_msg 
    finally:
    
        if con:
            con.close()
                 
#------------------------------------------------------------------------------
def db_exec_commad(command):
#------------------------------------------------------------------------------

    try:

        con = db_get_connection()
        cur = con.cursor()
        cur.execute(command)
        con.commit()
      
    except psycopg2.DatabaseError, e:          
    
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
        err_msg = "Unexpected error:", sys.exc_info()[0]
        print "ERROR:", err_msg 
    finally:
    
        if con:
            con.close()        
            
#------------------------------------------------------------------------------
def copy_file_to_table(file_name, target_table):
#------------------------------------------------------------------------------

    #print file_pattern
    try:
        #to use any file in pattern
        #file_name = max(glob.iglob(file_pattern), key=os.path.getctime)
        
        print "file size", os.path.getsize(file_name)
    
        copy_cmd = "\copy {0} from '{1}' WITH DELIMITER ',' CSV HEADER".format(target_table, os.path.abspath(file_name))
        #copy_cmd = "--delete --fields-terminated-by=',' --fields-optionally-enclosed-by='\"' --ignore-lines=1 trend {0}".format(file_name)
        # --verbose 
        #print copy_cmd
        
        psql_cmd = db_get_connection_command() + " -c\"" + copy_cmd + "\" -a"   
        
        #sql_cmd = db_get_import_command() + " " + copy_cmd   
        print psql_cmd
        retcode = call(psql_cmd, shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
    
        print 'Copied ' + file_name

    except IOError, e:    

        print 'Error %s' % e   
        sys.exit(1)
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e
            
    except:
        err_msg = "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "ERROR:", err_msg 
            