import os
import argparse

import time
import numpy as np
import pandas as pd
from datetime import date

parser = argparse.ArgumentParser(
                    prog='create_update_maxerf_risetime.py',
                    description='Create SQL files for updating qc.panels table with new max_erf and risetime data',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--comment', required=True, help='Comment that will be added to the entry in the reparis table')
parser.add_argument('--datafiles', nargs='*', help='csv files with the max_erf and risetime data you want to upload')



def read_csvs(csv):
    return pd.read_csv(csv, header=None, names=["ch", "rise_time", "max_erf_fit"])

def get_panel_id_from_csvfilename(csv):
    return int(csv.split('/')[-1].split('_')[0].replace('mn', ''))


args = parser.parse_args()
dict_args = vars(args) # convert to dictionary
csvfiles=dict_args['datafiles']
comment=dict_args['comment']
panel_id=0
for arg in csvfiles:
    if (panel_id==0): # get the panel number
        panel_id = get_panel_id_from_csvfilename(arg)
#        print("Panel ID = ", panel_id);
    else:
        if (get_panel_id_from_csvfilename(arg) != panel_id): # check that the files are all from the same panel
            print("ERROR: " + arg + " does not have the same panel_id as the first csv file (" + str(panel_id) + "). Exiting...")
            exit(1)

#    csvfiles.append(arg)

outfilename = '../sql/update_maxerf_risetime.sql';
print("Creating " + outfilename + " for panel number " + str(panel_id) + "...");

output_line = "Using data files: ";
for datafile in csvfiles:
    output_line += datafile + " ";
print(output_line)
df = pd.concat(map(read_csvs, csvfiles)) # (panel_datafiles, header=None);

# Now remove the leading directories from the csvfiles
nodir_csvfiles=[]
for csvfile in csvfiles:
    nodir_csvfiles.append(csvfile.split('/')[-1])

# Check we have 48 doublet-channels
expected_rows = 48;
if (len(df.index) != expected_rows):
    print("ERROR: Wrong number of rows. Expected " + str(expected_rows) + " but got " + str(len(df.index)) + ". Exiting...");
    exit(1);

# Check that we have no duplicate channels
if (df.duplicated('ch').any()):
    print("ERROR: There are duplicated channel numbers. Exiting...")
    exit(1);


#print(df.sort_values('ch').values)
#print(df.head())
#print(df.sort_values('ch')['rise_time'].to_numpy())
#print(df.sort_values('ch')['rise_time'].to_string(index=False).replace("\n", ","))

update_sql_file = open(outfilename, 'w')

# get the old values from qc.panels and create a new row in repairs.panels
update_sql_file.write("WITH old_values AS (SELECT panel_id,max_erf_fit from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,max_erf_fit FROM old_values;\n"); # insert the new repair row with the old values
update_sql_file.write("UPDATE qc.panels SET max_erf_fit=\'{" + df.sort_values('ch')['max_erf_fit'].to_string(index=False).replace("\n", ",") + "}\' where panel_id=" + str(panel_id) + ";\n");
# now update repairs table
update_sql_file.write("UPDATE repairs.panels SET column_changed=\'max_erf_fit\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
update_sql_file.write("WITH new_values AS (SELECT panel_id,max_erf_fit from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT max_erf_fit FROM new_values) WHERE repair_id=LASTVAL();\n"); # now add the new_values to the repair row

update_sql_file.write("WITH old_values AS (SELECT panel_id,rise_time from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,rise_time FROM old_values;\n"); # insert the new repair row with the old values
update_sql_file.write("UPDATE qc.panels SET rise_time=\'{" + df.sort_values('ch')['rise_time'].to_string(index=False).replace("\n", ",") + "}\' where panel_id=" + str(panel_id) + ";\n");
update_sql_file.write("UPDATE repairs.panels SET column_changed=\'rise_time\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
update_sql_file.write("WITH new_values AS (SELECT panel_id,rise_time from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT rise_time FROM new_values) WHERE repair_id=LASTVAL();\n"); # now add the new_values to the repair row


update_sql_file.write("WITH old_values AS (SELECT panel_id,maxerf_risetime_filenames from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,maxerf_risetime_filenames FROM old_values;\n"); # insert the new repair row with the old values
update_sql_file.write("UPDATE qc.panels SET maxerf_risetime_filenames=\'{"
                      + ' '.join([csvfile+"," for csvfile in nodir_csvfiles[:-1]]) # all but the last filenames should be comma-separated
                      + ' '.join([csvfile for csvfile in nodir_csvfiles[-1:]])
                      + "}\' where panel_id=" + str(panel_id) + ";\n");
update_sql_file.write("UPDATE repairs.panels SET column_changed=\'maxerf_risetime_filenames\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
update_sql_file.write("WITH new_values AS (SELECT panel_id,maxerf_risetime_filenames from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT maxerf_risetime_filenames FROM new_values) WHERE repair_id=LASTVAL();\n"); # now add the new_values to the repair row
print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb11 -p 5459 mu2e_tracker_prd < " + outfilename)
