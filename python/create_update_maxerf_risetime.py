import os

def usage():
    print("Usage: python3 create_update_maxerf_risetime.py file1.csv file2.csv ...")
#    print("All the csv files
    exit(1);

if (len(os.sys.argv) < 2):
    usage()
elif (os.sys.argv[1] == "-h" or os.sys.argv[1] == "--help"):
    usage()

import time
import numpy as np
import pandas as pd


def read_csvs(csv):
    return pd.read_csv(csv, header=None, names=["ch", "rise_time", "max_erf_fit"])

def get_panel_id_from_csvfilename(csv):
    return int(csv.split('/')[-1].split('_')[0].replace('mn', ''))


csvfiles=[]
panel_id=0
for arg in os.sys.argv[1:]:
    if (panel_id==0): # get the panel number
        panel_id = get_panel_id_from_csvfilename(arg)
#        print("Panel ID = ", panel_id);
    else:
        if (get_panel_id_from_csvfilename(arg) != panel_id): # check that the files are all from the same panel
            print("ERROR: " + arg + " does not have the same panel_id as the first csv file (" + str(panel_id) + "). Exiting...")
            exit(1)

    csvfiles.append(arg)

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
update_sql_file.write("UPDATE qc.panels SET max_erf_fit=\'{" + df.sort_values('ch')['max_erf_fit'].to_string(index=False).replace("\n", ",") + "}\' where panel_id=" + str(panel_id) + ";\n");
update_sql_file.write("UPDATE qc.panels SET rise_time=\'{" + df.sort_values('ch')['rise_time'].to_string(index=False).replace("\n", ",") + "}\' where panel_id=" + str(panel_id) + ";\n");
update_sql_file.write("UPDATE qc.panels SET maxerf_risetime_filenames=\'{"
                      + ' '.join([csvfile+"," for csvfile in nodir_csvfiles[:-1]]) # all but the last filenames should be comma-separated
                      + ' '.join([csvfile for csvfile in nodir_csvfiles[-1:]])
                      + "}\' where panel_id=" + str(panel_id) + ";\n");
print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb08 -p 5459 mu2e_tracker_prd < " + outfilename)
