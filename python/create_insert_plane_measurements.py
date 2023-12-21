import os
import argparse

import time
import numpy as np
import pandas as pd
from datetime import date

measurements={ 'heights' : ["phi_location_deg", "height_inches"]}

parser = argparse.ArgumentParser(
                    prog='create_insert_plane_measurements.py',
                    description='Create SQL files for inserting new data into measurements.panel_* tables',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--plane_id', required=True)
parser.add_argument('--measurement_type', required=True, choices=measurements.keys(), help='the type of measurement')
parser.add_argument('--datafile', required=True, help='csv file with the data you want to upload. The columns for each measurement type are:'+str(measurements))
parser.add_argument('--date_taken', required=True, help='date the data was taken (format: \'yyyy-mm-dd\')')



def read_csvs(csv): #, cols):
    return pd.read_csv(csv)


args = parser.parse_args()
dict_args = vars(args) # convert to dictionary

plane_id=args.plane_id
measurement_type =args.measurement_type
datafile=args.datafile
date_taken=args.date_taken


data = read_csvs(datafile) #, cols)

cols = measurements[args.measurement_type]

output_line = "Using data file: " + datafile;
print(output_line)

outfilename = '../sql/insert_plane_measurements.sql';
print("Creating " + outfilename + " for plane number " + str(plane_id) + "...");

insert_sql_file = open(outfilename, 'w')

insert_sql_file.write('INSERT INTO measurements.plane_'+measurement_type+'(plane_id, '+', '.join(cols)+', date_taken) VALUES')

last_index = len(data)
for index,row in data.iterrows():
    insert_sql_file.write('\n('+str(plane_id)+', ');
    for col in cols:
        insert_sql_file.write(str(row[col])+', ');
    insert_sql_file.write('\''+date_taken+'\')')

    if (index == last_index-1):
        insert_sql_file.write(';')
    else:
        insert_sql_file.write(',')

# # get the old values from qc.panels and create a new row in repairs.panels
# update_sql_file.write("WITH old_values AS (SELECT panel_id,max_erf_fit from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,max_erf_fit FROM old_values;\n"); # insert the new repair row with the old values
# update_sql_file.write("UPDATE qc.panels SET max_erf_fit=\'{" + df.sort_values('ch')['max_erf_fit'].to_string(index=False).replace("\n", ",") + "}\' where panel_id=" + str(panel_id) + ";\n");
# # now update repairs table
# update_sql_file.write("UPDATE repairs.panels SET column_changed=\'max_erf_fit\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
# update_sql_file.write("WITH new_values AS (SELECT panel_id,max_erf_fit from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT max_erf_fit FROM new_values) WHERE repair_id=LASTVAL();\n"); # now add the new_values to the repair row

# update_sql_file.write("WITH old_values AS (SELECT panel_id,rise_time from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,rise_time FROM old_values;\n"); # insert the new repair row with the old values
# update_sql_file.write("UPDATE qc.panels SET rise_time=\'{" + df.sort_values('ch')['rise_time'].to_string(index=False).replace("\n", ",") + "}\' where panel_id=" + str(panel_id) + ";\n");
# update_sql_file.write("UPDATE repairs.panels SET column_changed=\'rise_time\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
# update_sql_file.write("WITH new_values AS (SELECT panel_id,rise_time from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT rise_time FROM new_values) WHERE repair_id=LASTVAL();\n"); # now add the new_values to the repair row


# update_sql_file.write("WITH old_values AS (SELECT panel_id,plane_measurements_filenames from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,plane_measurements_filenames FROM old_values;\n"); # insert the new repair row with the old values
# update_sql_file.write("UPDATE qc.panels SET plane_measurements_filenames=\'{"
#                       + ' '.join([csvfile+"," for csvfile in nodir_csvfiles[:-1]]) # all but the last filenames should be comma-separated
#                       + ' '.join([csvfile for csvfile in nodir_csvfiles[-1:]])
#                       + "}\' where panel_id=" + str(panel_id) + ";\n");
# update_sql_file.write("UPDATE repairs.panels SET column_changed=\'plane_measurements_filenames\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
# update_sql_file.write("WITH new_values AS (SELECT panel_id,plane_measurements_filenames from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT plane_measurements_filenames FROM new_values) WHERE repair_id=LASTVAL();\n"); # now add the new_values to the repair row
print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb08 -p 5459 mu2e_tracker_prd < " + outfilename)
