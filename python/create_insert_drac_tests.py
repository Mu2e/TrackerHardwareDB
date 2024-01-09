import os
import argparse

import time
import numpy as np
import pandas as pd
from datetime import date
import json

parser = argparse.ArgumentParser(
                    prog='create_insert_drac_tests.py',
                    description='Create SQL files for inserting new data into drac tables',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--datafile', required=True, help='json file with the data you want to upload (must include folder name).')


args = parser.parse_args()
dict_args = vars(args) # convert to dictionary

datafile=args.datafile

panel_id='UNKNOWN'
drac_id='UNKNOWN'
if datafile.find('/') == -1:
    print("ERROR: --datafile must contain the foldername with the drac ID and panel number")
    print("Exiting...")
    exit(1);

# Try to determine the panel_id and drac_id from the folder name
panel_and_drac = datafile.split('/')[-2] # -1 is the filename, -2 is the folder name we want
panel_id=panel_and_drac.split('_')[1] # format = "Panel_[panel_id]_ROC_[drac_id]"
drac_id=panel_and_drac.split('_')[3]

if panel_id=='UNKNOWN':
    print("ERROR: Could not determine panel_id from \""+datafile+"\"")
    print("Exiting...")
    exit(1);

if drac_id=='UNKNOWN':
    print("ERROR: Could not determine drac_id from \""+datafile+"\"")
    print("Exiting...")
    exit(1);

print("Panel ID = " + panel_id)
print("DRAC ID = " + drac_id)

json_file = open(datafile)
data = json.load(json_file)
#data = pd.read_json(datafile) #, cols)

output_line = "Using data file: " + datafile;
print(output_line)

outfilename = '../sql/insert_drac_tests.sql';
print("Creating " + outfilename + "...");

insert_sql_file = open(outfilename, 'w')

# ROC configuration
insert_sql_file.write('INSERT INTO drac.roc_configs(device_serial,design_info,design_ver,back_level_ver) VALUES\n')
roc_config = data['ROC']
insert_sql_file.write('(\''+roc_config['DeviceSerial'] + '\', ')
insert_sql_file.write('\''+roc_config['DesignInfo'] + '\', ')
insert_sql_file.write('\''+roc_config['DesignVer'] + '\', ')
insert_sql_file.write('\''+roc_config['BackLevelVer'] + '\'')
insert_sql_file.write(')\n')
insert_sql_file.write('ON CONFLICT (device_serial,design_info,design_ver,back_level_ver) DO NOTHING;\n') # this line means it won't insert this row if an identical row already exists

# CAL configuration
insert_sql_file.write('\nINSERT INTO drac.cal_configs(id_read, silsig, design_name, checksum, design_info, design_ver, back_level, debug_info, dsn) VALUES\n')
cal_config = data['CAL']
for field in cal_config:
    cal_config[field] = cal_config[field][1:] # remove the '\u' character from the values
insert_sql_file.write('(\''+cal_config['ID read']+ '\', ')
insert_sql_file.write('\''+cal_config['SILSIG'] + '\', ')
insert_sql_file.write('\''+cal_config['Design Name'] + '\', ')
insert_sql_file.write('\''+cal_config['Checksum'] + '\', ')
insert_sql_file.write('\''+cal_config['Design Info'] + '\', ')
insert_sql_file.write('\''+cal_config['DESIGNVER'] + '\', ')
insert_sql_file.write('\''+cal_config['BACKLEVEL'] + '\', ')
insert_sql_file.write('\''+cal_config['Debug Info'] + '\', ')
insert_sql_file.write('\''+cal_config['DSN'] + '\'')
insert_sql_file.write(')\n')
insert_sql_file.write('ON CONFLICT (id_read, silsig, design_name, checksum, design_info, design_ver, back_level, debug_info, dsn) DO NOTHING;\n') # this line means it won't insert this row if an identical row already exists

# HV configuration
insert_sql_file.write('\nINSERT INTO drac.hv_configs(id_read, silsig, design_name, checksum, design_info, design_ver, back_level, debug_info, dsn) VALUES\n')
hv_config = data['HV']
for field in hv_config:
    hv_config[field] = hv_config[field][1:] # remove the '\u' character from the values
insert_sql_file.write('(\''+hv_config['ID read']+ '\', ')
insert_sql_file.write('\''+hv_config['SILSIG'] + '\', ')
insert_sql_file.write('\''+hv_config['Design Name'] + '\', ')
insert_sql_file.write('\''+hv_config['Checksum'] + '\', ')
insert_sql_file.write('\''+hv_config['Design Info'] + '\', ')
insert_sql_file.write('\''+hv_config['DESIGNVER'] + '\', ')
insert_sql_file.write('\''+hv_config['BACKLEVEL'] + '\', ')
insert_sql_file.write('\''+hv_config['Debug Info'] + '\', ')
insert_sql_file.write('\''+hv_config['DSN'] + '\'')
insert_sql_file.write(')\n')
insert_sql_file.write('ON CONFLICT (id_read, silsig, design_name, checksum, design_info, design_ver, back_level, debug_info, dsn) DO NOTHING;\n') # this line means it won't insert this row if an identical row already exists


# Insert the test results
# First, get the config IDs for the ROC, CAL, and HV FPGAs
roc_config_id_select="(SELECT roc_config_id from drac.roc_configs where device_serial=\'"+roc_config['DeviceSerial']+"\' and design_info=\'"+roc_config['DesignInfo']+"\' and design_ver=\'"+roc_config['DesignVer']+"\' and back_level_ver=\'"+roc_config['BackLevelVer']+"\')"
cal_config_id_select="(SELECT cal_config_id from drac.cal_configs where id_read=\'"+cal_config['ID read']+"\' and silsig=\'"+cal_config['SILSIG']+"\' and design_name=\'"+cal_config['Design Name']+"\' and checksum=\'"+cal_config['Checksum']+"\' and design_info=\'"+cal_config['Design Info']+"\' and design_ver=\'"+cal_config['DESIGNVER']+"\' and back_level=\'"+cal_config['BACKLEVEL']+"\' and debug_info=\'"+cal_config['Debug Info']+"\' and dsn=\'"+cal_config['DSN']+"\')"
hv_config_id_select="(SELECT hv_config_id from drac.hv_configs where id_read=\'"+hv_config['ID read']+"\' and silsig=\'"+hv_config['SILSIG']+"\' and design_name=\'"+hv_config['Design Name']+"\' and checksum=\'"+hv_config['Checksum']+"\' and design_info=\'"+hv_config['Design Info']+"\' and design_ver=\'"+hv_config['DESIGNVER']+"\' and back_level=\'"+hv_config['BACKLEVEL']+"\' and debug_info=\'"+hv_config['Debug Info']+"\' and dsn=\'"+hv_config['DSN']+"\')"

# Get the Board Status test results
board_status_dict = { 'I3.3' : "I3_3",
                      'I2.5' : "I2_5",
                      'I1.8HV' : "I1_8HV",
                      'IHV5.0' : "IHV5_0",
                      'VDMBHV5.0' : "VDMBHV5_0",
                      'V1.8HV' : "V1_8HV",
                      'V3.3HV' : "V3_3HV",
                      'V2.5' : "V2_5",
                      'A0' : "A0",
                      'A1' : "A1",
                      'A2' : "A2",
                      'A3' : "A3",
                      'I1.8CAL' : "I1_8CAL",
                      'I1.2' : "I1_2",
                      'ICAL5.0' : 'ICAL5_0',
                      'ADCSPARE' : 'ADCSPARE',
                      'V3.3' : 'V3_3',
                      'VCAL5.0' : 'VCAL5_0',
                      'V1.8CAL' : 'V1_8CAL',
                      'V1.0' : 'V1_0',
                      'ROCPCBTEMP' : 'ROCPCBTEMP',
                      'HVPCBTEMP' : 'HVPCBTEMP',
                      'CALPCBTEMP' : 'CALPCBTEMP',
                      'RTD' : 'RTD',
                      'ROC_RAIL_1V(mV)' : 'ROC_RAIL_1V_mV',
                      'ROC_RAIL_1.8V(mV)' : 'ROC_RAIL_1_8V_mV',
                      'ROC_RAIL_2.5V(mV)' : 'ROC_RAIL_2_5V_mV',
                      'ROC_TEMP(CELSIUS)' : 'ROC_TEMP_degC',
                      'CAL_RAIL_1V(mV)' : 'CAL_RAIL_1V_mV',
                      'CAL_RAIL_1.8V(mV)' : 'CAL_RAIL_1_8V_mV',
                      'CAL_RAIL_2.5V(mV)' : 'CAL_RAIL_2_5V_mV',
                      'CAL_TEMP(CELSIUS)' : 'CAL_TEMP_degC',
                      'HV_RAIL_1V(mV)' : 'HV_RAIL_1V_mV',
                      'HV_RAIL_1.8V(mV)' : 'HV_RAIL_1_8V_mV',
                      'HV_RAIL_2.5V(mV)' : 'HV_RAIL_2_5V_mV',
                      'HV_TEMP(CELSIUS)' : 'HV_TEMP_degC',
                      'TEMP[degC]' : 'TEMP_degC',
                      '2.5V': 'VOLT_2_5V',
                      '5.1V' : 'VOLT_5_1V'
}
board_status = data['BoardStatus']
board_status_values=[]
for json_field in board_status_dict:
    board_status_values.append(str(board_status[json_field]))


# Get the pulser results
pulser_rates = data['PulserRates']
pulser_total_hv = "\'{";
n_channels = 96;
for i_channel in range(0, n_channels):
    pulser_total_hv += str(pulser_rates[str(i_channel)]["TotalHV"]);
    if i_channel != n_channels-1:
        pulser_total_hv += ", "
pulser_total_hv += "}\'"


# Now insert the data
insert_sql_file.write("\nINSERT INTO drac.test_results(drac_id, panel_id, roc_config_id, cal_config_id, hv_config_id, "+', '.join(board_status_dict.values())+", pulser_total_hv) VALUES\n")
insert_sql_file.write("(\'"+drac_id+"\', "+panel_id+", "+roc_config_id_select+", "+cal_config_id_select+", " + hv_config_id_select+", "+', '.join(board_status_values)+", "+pulser_total_hv+");")


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
