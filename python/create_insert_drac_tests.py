import os
import argparse

import time
import numpy as np
import pandas as pd
from datetime import date
import json

measurements={ 'leaks' : ["panel_id", "leak_sccm", "comment"]}

parser = argparse.ArgumentParser(
                    prog='create_insert_drac_tests.py',
                    description='Create SQL files for inserting new data into drac tables',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--datafile', required=True, help='json file with the data you want to upload.')


def read_csvs(csv): #, cols):
    return pd.read_csv(csv)


args = parser.parse_args()
dict_args = vars(args) # convert to dictionary

datafile=args.datafile

json_file = open(datafile)
data = json.load(json_file)
#data = pd.read_json(datafile) #, cols)

output_line = "Using data file: " + datafile;
print(output_line)

outfilename = '../sql/insert_drac_tests.sql';
print("Creating " + outfilename + "...");

insert_sql_file = open(outfilename, 'w')

insert_sql_file.write('INSERT INTO drac.roc_configs(device_serial,design_info,design_ver,back_level_ver) VALUES\n')
roc_config = data['ROC']
insert_sql_file.write('(\''+roc_config['DeviceSerial'] + '\', ')
insert_sql_file.write('\''+roc_config['DesignInfo'] + '\', ')
insert_sql_file.write('\''+roc_config['DesignVer'] + '\', ')
insert_sql_file.write('\''+roc_config['BackLevelVer'] + '\'')
insert_sql_file.write(')\n')
insert_sql_file.write('ON CONFLICT (device_serial,design_info,design_ver,back_level_ver) DO NOTHING;')


# cal_config = data['CAL']
# for field in cal_config:
#     print(field, cal_config[field])

# hv_config = data['HV']
# for field in hv_config:
#     print(field, hv_config[field])

# board_status = data['BoardStatus']
# for field in board_status:
#     print(field, board_status[field])

# pulser_rates = data['PulserRates']
# for channel in pulser_rates:
#     for count in pulser_rates[channel]:
#         print(channel, count, pulser_rates[channel][count])

# deltat_rms = data['deltatRMS']
# for channel,i_deltat_rms in enumerate(deltat_rms):
#     print(channel, i_deltat_rms)

# preamp_settings = data['PreampSettings']
# #print(preamp_settings)
# for i,field in enumerate(preamp_settings):
#     print(i, field)

# preamp_thresholds = data['PreampThresholds']
# print(preamp_thresholds)
# for channel in preamp_thresholds:
#     print(channel, preamp_thresholds[channel])

# cols = measurements[args.measurement_type]

# output_line = "Using data file: " + datafile;
# print(output_line)

# outfilename = '../sql/insert_drac_tests.sql';
# print("Creating " + outfilename + "...");

# insert_sql_file = open(outfilename, 'w')

# insert_sql_file.write('INSERT INTO measurements.panel_'+measurement_type+'('+', '.join(cols)+', date_taken) VALUES')

# last_index = len(data)
# for index,row in data.iterrows():
#     insert_sql_file.write('\n(')
#     for col in cols:
#         insert_sql_file.write(str(row[col])+', ');
#     insert_sql_file.write('\''+date_taken+'\')')

#     if (index == last_index-1):
#         insert_sql_file.write(';')
#     else:
#         insert_sql_file.write(',')

# # # get the old values from qc.panels and create a new row in repairs.panels
# # update_sql_file.write("WITH old_values AS (SELECT panel_id,max_erf_fit from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,max_erf_fit FROM old_values;\n"); # insert the new repair row with the old values
# # update_sql_file.write("UPDATE qc.panels SET max_erf_fit=\'{" + df.sort_values('ch')['max_erf_fit'].to_string(index=False).replace("\n", ",") + "}\' where panel_id=" + str(panel_id) + ";\n");
# # # now update repairs table
# # update_sql_file.write("UPDATE repairs.panels SET column_changed=\'max_erf_fit\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
# # update_sql_file.write("WITH new_values AS (SELECT panel_id,max_erf_fit from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT max_erf_fit FROM new_values) WHERE repair_id=LASTVAL();\n"); # now add the new_values to the repair row

# # update_sql_file.write("WITH old_values AS (SELECT panel_id,rise_time from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,rise_time FROM old_values;\n"); # insert the new repair row with the old values
# # update_sql_file.write("UPDATE qc.panels SET rise_time=\'{" + df.sort_values('ch')['rise_time'].to_string(index=False).replace("\n", ",") + "}\' where panel_id=" + str(panel_id) + ";\n");
# # update_sql_file.write("UPDATE repairs.panels SET column_changed=\'rise_time\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
# # update_sql_file.write("WITH new_values AS (SELECT panel_id,rise_time from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT rise_time FROM new_values) WHERE repair_id=LASTVAL();\n"); # now add the new_values to the repair row


# # update_sql_file.write("WITH old_values AS (SELECT panel_id,drac_tests_filenames from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,drac_tests_filenames FROM old_values;\n"); # insert the new repair row with the old values
# # update_sql_file.write("UPDATE qc.panels SET drac_tests_filenames=\'{"
# #                       + ' '.join([csvfile+"," for csvfile in nodir_csvfiles[:-1]]) # all but the last filenames should be comma-separated
# #                       + ' '.join([csvfile for csvfile in nodir_csvfiles[-1:]])
# #                       + "}\' where panel_id=" + str(panel_id) + ";\n");
# # update_sql_file.write("UPDATE repairs.panels SET column_changed=\'drac_tests_filenames\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
# # update_sql_file.write("WITH new_values AS (SELECT panel_id,drac_tests_filenames from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT drac_tests_filenames FROM new_values) WHERE repair_id=LASTVAL();\n"); # now add the new_values to the repair row
print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb08 -p 5459 mu2e_tracker_prd < " + outfilename)
