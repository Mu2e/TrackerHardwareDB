import os
import time
import pandas as pd
import psycopg2
import numpy as np

from qc_panels_columns import single_ch_issues

def usage():
    print("Usage: python3 create_imported_ATD_spreadsheet.py ATD_spreadsheet.csv YYYY_MM_DD")
    print("where YYYY_MM_DD is the snapshot date")
    exit(1);

def replace_problem_chars(string):
    return string.replace(' ', '_').replace('.', '').replace('\'', '').replace("&", "and").replace("-", '').replace("(", '').replace(")", '').replace(":","_").replace(',', '_').replace('?','');

def get_qc_db_panel_info(cur, panel_id, issue):
    query = 'SELECT '+ issue + ' FROM qc.panels WHERE panel_id='+panel_id+';'
    cur.execute(query)
    rows = cur.fetchall()
    conn.commit()
    if (len(rows) == 0):
        print("ERROR: Received no rows from QC database\n\t Query: \"" + query + "\"")
        exit(1);
    elif (len(rows) != 1):
        print("ERROR: Received more than one row from QC database\n\t Query: \"" + query + "\"")
        exit(1);
    # There should only be one row corresponding to a single panel and this function is for a single issue so return just the list of channel numbers
    return rows[0][0]

if (len(os.sys.argv) != 3):
    usage()
elif (os.sys.argv[1] == "-h" or os.sys.argv[1] == "--help"):
    usage()

csvfile=os.sys.argv[1]
if (not os.path.exists(csvfile)):
    print("CSV file \"" + csvfile + "\" does not exist. Exiting...");
    exit(1);

snapshot_date=os.sys.argv[2]
if ("_" not in snapshot_date):
    print("Format should be YYYY_MM_DD. Exiting...")
    exit(1)


# A dictionary to map the "Problem" in the ATD spreadsheet to the column name in qc.panels
ATD_to_DB_issue_dict = { "Patched straw" : "patched_straws",
                         "Short wire" : "short_wires",
                         "Loose preamp-AMB connection" : "loose_preamp_amb_connections",
                         "High current" : "high_current_wires",
                         "High Current" : "high_current_wires",
                         "High current " : "high_current_wires",
                         "Sparks" : "sparking_wires",
                         "Low anode-to-cathode resistance" : "low_anode_cathode_resistances",
                         "Missing straw" : "missing_straws",
                         "Missing wire" : "missing_wires",
                         "Missing anode" : "missing_anode",
                         "Missing Anode Pin" : "missing_anode",
                         "Loose preamp-anode connection" : "loose_preamp_anode_connections",
                         "Suspicious preamp threshold" : "suspicious_preamp_thresholds",
                         "Short between contiguous omega pieces" : "short_omega_pieces",
                         "Blocked straw" : "blocked_straws",
                         "Blocked Straw" : "blocked_straws",
                         "Jumper-DMB connection" : "bad_jumper_dmb_connection",
                         "No high voltage on CAL side" : "no_hv_straw_cal",
                         "No HV straw CAL" : "no_hv_straw_cal",
                         "Preamp-AMB LV short" : "preamp_amb_lv_short",
                         "DMB damage" : "bad_dmb_channel_connection",
                         "Missing omega piece" : "missing_omega_pieces",
                         "Bad calibration pulses" : "bad_calibration_pulses",
                         "Kapton dots" : "kapton_dots",
                         "CAL insertion from AMB" : "cal_insertion_from_amb",
                         "Problem" : "problem",
                         "Loose/Wiggly CAL Anode" : "loose_cal_anode",
                         "Loose/wiggly HV anode" : "loose_hv_anode",
                         "Unable to meet LV thresholds" : "unable_to_meet_lv_thresholds",
                         "Missing anode pin" : "missing_anode",
                         "Sparking Wire Cal-side" : "sparking_cal",
                         "Intermittent Rates" : "intermittent_rates",
                         "Missing calpulse on DPT" : "bad_calibration_pulses",
                         "No CAL Pulse Rates" : "bad_calibration_pulses",
                         "Noise" : "noisy_channels",
                         "No Coincidences" : "no_coincidences"
                        }

# Connect to the DB to see what is already in there
USER=os.environ.get('USER')
conn = psycopg2.connect(database = "mu2e_tracker_prd",
                        user = USER,
                        host= 'ifdb11',
                        port = 5459)
cur = conn.cursor()

most_recent=0.
#print(csvfile)

bash_script_name = 'update_qc_panels_from_ATD_spreadsheet.sh'
bash_script = open(bash_script_name, 'w')
bash_script.write('#!/bin/bash\n')
bash_script.write("rm ../sql/update_qc_panels_table.sql\n")

all_contents=[]
#
# Here we read in the CSV file and do some cleaning
#
pd.options.mode.copy_on_write = True
df = pd.read_csv(csvfile)

# Do some proecessing that will also be useful when we copy the csv file to the database
# Then, forward fill some columns because the original spreadsheet used merged cells
df['Panel'] = df[['Panel']].ffill()
df['Install No.'] = df[['Install No.']].ffill()
df['Production No.'] = df[['Production No.']].ffill()
# Split plane number and side A/B
df[['Plane', 'Side']] = df['Production No.'].str.split(' ', n=1, expand=True)

# Now save this version for importing later
filled_csvfile="ATD_spreadsheet_filled.csv"
df.to_csv(filled_csvfile, index=False);
all_columns = df.columns.tolist()
#print(all_columns)

# For the rest of the script, we don't need these columns
# First remove rows with panel number and channel number that are NaNs
df = df.dropna(subset=['Panel', 'Channel', 'Problem'], how='all')
df = df.drop(['Install No.', 'Connected', 'Disonnected', 'Unnamed: 11'], axis=1)

#pd.set_option('display.width', None)
#print(df.head())

print("\nChecking that panel_ids for each plane are the same in ATD spreadsheet and QC database...")

plane_grouped  = df.groupby(['Plane'])
all_planes = np.linspace(1,36, 36, dtype=int)
planes_checked = []
for name, group in plane_grouped:
#    print(name)
#    print(group)
    plane_id = int(name[0][:2])
    atd_panel_ids = set([int(panel[2:]) for panel in group['Panel'].tolist()]) # make it a "set" to remove duplicates
#    print(plane_id, atd_panel_ids)
    query = 'SELECT panel_ids FROM qc.planes WHERE plane_id='+str(plane_id)+';'
    cur.execute(query)
    rows = cur.fetchall()
    conn.commit()
    if (len(rows) == 0):
        print("ERROR: Received no rows from QC database\n\t Query: \"" + query + "\"")
        break;
    elif (len(rows) != 1):
        print("ERROR: Received more than one row from QC database\n\t Query: \"" + query + "\"")
        break;
    # There should only be one row corresponding to a single panel
    row = rows[0]
    qc_db_panel_ids = set(row[0])
#    print(qc_db_panel_ids)
    if qc_db_panel_ids != atd_panel_ids:
        print("!!! Plane "+str(plane_id) + " panel_ids are NOT the same (ATD: " + str(atd_panel_ids) + ", QC DB: " + str(qc_db_panel_ids) + ") !!!")
        exit(1)
#    else:
#        print("Plane "+str(plane_id) + " panel_ids are the same (ATD: " + str(atd_panel_ids) + ", QC DB: " + str(qc_db_panel_ids) + ")")
    planes_checked.append(plane_id)
    #break

# Make sure that we have all planes
missing_planes = set(all_planes) - set(planes_checked)
if (len(missing_planes)>0):
    print("!!! We are missing planes " + str(missing_planes))
    exit(1)
print("...Done!\n")

# First get the panels with no issues and make sure that QC DB agrees
print("\nChecking that panels with no issues in ATD spreadsheet also have no problems in QC database...")
no_problem_panels = df.loc[df['Seen in QC, E-installation, or CuClips Installation?']=="No problems"]
panel_ok = True
skip = False
for index,row in no_problem_panels.iterrows():
    panel_id = row['Panel'][2:] # need to remove "MN" from front of string for DB
    for issue in single_ch_issues:
        result = get_qc_db_panel_info(cur, panel_id, issue)
        if len(sorted(result)) > 0:
            print("!!! MN" + panel_id + " was reported as having no problems in the ATD spreadsheet but has the following channels with issue \"" + issue + "\" in the QC DB: " + str(result))
            user_check = ""
            while user_check not in ['y', 'n', 'Y', 'N', 's', 'S']:
                user_check = input("Check the Panel QC webpage and look at the traveler for panel "+panel_id+". Should these values be removed from the QC database? (y/n/s=skip to next stage) ")
            panel_ok = False

            if user_check in ['y', 'Y']:
                bash_script.write("python3")
            elif user_check in ['s', 'S']:
                skip = True
                break
    if skip:
        break
    if panel_ok:
        print("MN" + panel_id + ": OK")



# Now check the panels with problems. Remove the "no_problem_panels" so we can forward-fill channel numbers
print("\nChecking remaining panels...")
df = df[df['Seen in QC, E-installation, or CuClips Installation?']!="No problems"]
df['Channel'] = df[['Channel']].ffill()
#print(df[(df['Panel']=="MN026")])
# Convert the ATD "Problem" to the QC DB "Issue" here so that we can collect
# ATD problems that map to the same issue (e.g. due to different capitalizations)
df['QC DB Issue'] = df['Problem'].map(ATD_to_DB_issue_dict)

unaccounted_for_problems = df[(df['QC DB Issue'].isna()) & ((~df['Problem'].isna()) & (df['Problem'] != '-'))][['Problem', "QC DB Issue"]]
if len(unaccounted_for_problems) != 0:
    print(unaccounted_for_problems.head(20))
    print("ERROR: Some problems in the ATD spreadsheet do not have a defined equivalent in the QC DB (see above for list)")
    exit(1)
grouped = df.groupby(['Panel', 'QC DB Issue'])
#print(df.keys())
#print(df.head(10))
for name, group in grouped:
    panel_id = name[0][2:] # need to remove "MN" from front of string for DB
    if name[1] == "-" or name[1] == "no problem":
        # There are no problems
        continue
    issue = name[1]
    # These are columns I still need to add
    if issue in ['problem']:
        print("TODO: Skipping issue "+issue+ " because it is not yet in QC DB")
        continue

#    print(name, group)
    channel_list = group['Channel'].tolist()
    if ("general" in channel_list or "  " in channel_list):
        print("ERROR: a string is in the channel colom (TODO)")
        continue
    atd_channels = sorted([int(ch) for ch in channel_list]) # channels with this problem in ATD spreadsheet
#    print(atd_channels)

    result = get_qc_db_panel_info(cur, panel_id, issue)
    qc_db_channels = sorted(result)
#    print(qc_db_channels)
    if qc_db_channels != atd_channels:
        channels_in_atd_not_in_qc_db = list(set(atd_channels) - set(qc_db_channels))
        channels_in_qc_db_not_in_atd = list(set(qc_db_channels) - set(atd_channels))
        print("!!! MN"+panel_id, issue, "channels are NOT the same (ATD: " + str(atd_channels) + ", QC DB: " + str(qc_db_channels) + ")");
        user_check = ""
        while user_check not in ['y', 'n', 'Y', 'N', 's', 'S']:
            user_check = input("I will make the following changes to the QC DB:  Add " + str(channels_in_atd_not_in_qc_db) + ". Remove: " + str(channels_in_qc_db_not_in_atd) + ". Check the Panel QC webpage and look at the traveler for panel "+panel_id+". Are these changes OK (y/n)? ")

        if user_check in ['s', 'S']:
            break
        
        if user_check in ['y', 'Y']:
            bash_script.write("python3 create_update_qc_panels_table.py --append=True --panel_id " + str(int(panel_id)))
            if (len(channels_in_qc_db_not_in_atd) > 0):
                bash_script.write(" --remove_"+issue+ " " +  " ".join(map(str, channels_in_qc_db_not_in_atd)))
            if (len(channels_in_atd_not_in_qc_db) > 0):
                bash_script.write(" --add_" + issue + " " + " ".join(map(str, channels_in_atd_not_in_qc_db)))
            bash_script.write(" --comment \'updated from ATD spreadsheet\'\n");
        elif user_check in ['n', 'N']:
            user_input = ""
            while user_input not in ['y', 'Y', 'n', 'N']:
                user_input = input("Should I leave the contents of the QC DB unchanged (y/n)? ")

            if user_input in ['y', 'Y']:
                print("Doing nothing for panel " + panel_id + " " + issue)
                continue
            else:
                user_check2 = "";
                channels_to_add = []
                channels_to_remove = []
                while user_check2 not in ['y', 'Y']:
                    user_input = input("Which channels should I add to QC DB column "+issue+"? ")
                    channels_to_add = list(map(int,user_input.split()))

                    user_input = input("Which channels should I remove from QC DB column "+issue+"? ")
                    channels_to_remove = list(map(int,user_input.split()))

                    final_qc_db_channels = list(set(qc_db_channels + channels_to_add) - set(channels_to_remove))
                    print("This will result in the QC DB containing [" + ", ".join(map(str,final_qc_db_channels)) + "]")
                    user_check2 = input("Is this right (y/n)? ")

                bash_script.write(" --add_" + issue + " " + " ".join(map(str,channels_to_add)))
                bash_script.write(" --remove_" + issue + " " + " ".join(map(str,channels_to_remove)))


#    else:
#        print("MN"+panel_id, issue, " channels are the same (ATD: " + str(atd_channels) + ", QC DB: " + str(qc_db_channels) + ")")
#    break
conn.close()

#
# Now store a copy of the ATD spreadsheet that we just read
#
sql_filename = '../sql/create_imported_ATD_spreadsheet.sql'
create_sql_file = open(sql_filename, 'w')
create_sql_file.write("set role mu2e_tracker_admin;\n")
create_sql_file.write("DROP TABLE imported.ATD_spreadsheet_previous;\n"); # drop the previous table (needed to check differences between now and last time)
create_sql_file.write("CREATE TABLE imported.ATD_spreadsheet_previous AS SELECT * FROM imported.ATD_spreadsheet;\n")
create_sql_file.write("GRANT SELECT ON imported.ATD_spreadsheet_previous TO public;\n");
create_sql_file.write("DROP TABLE imported.ATD_spreadsheet;\n"); # drop the current table, we will recreate it at the end
table_name = "imported.ATD_spreadsheet_"+snapshot_date
create_sql_file.write("CREATE TABLE "+table_name+"(");#(row serial primary key");
first_col=True
for col in all_columns:
    if not first_col:
        create_sql_file.write(", "); # don't want to write a comma for the first column
    else:
        first_col=False # just seen the first row
    create_sql_file.write(replace_problem_chars(col) + " text");
create_sql_file.write(");\n");
create_sql_file.write("\\copy "+table_name+" FROM \'"+filled_csvfile+"\' DELIMITER ',' CSV HEADER;\n");

create_sql_file.write("grant select on "+table_name+" to public;\n");
create_sql_file.write("grant insert on "+table_name+" to mu2e_tracker_admin;\n");
create_sql_file.write("CREATE TABLE imported.ATD_spreadsheet AS SELECT * FROM "+table_name+";\n")
create_sql_file.write("GRANT SELECT ON imported.ATD_spreadsheet TO public;")

print("Done!")
print("Now check " + bash_script_name + " looks OK and run it like this:")
print(" . ./" + bash_script_name);

print("Also check " + sql_filename + " looks OK and run it like this:")
print(" psql -h ifdb11 -p 5459 mu2e_tracker_prd < " + sql_filename);
