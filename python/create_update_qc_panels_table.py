import os
import argparse

import time
import numpy as np
import pandas as pd
from datetime import date

all_columns=['missing_straws', 'high_current_wires', 'blocked_straws', 'sparking_wires', 'no_hv_straw_hv', 'no_hv_straw_cal', 'missing_omega_pieces', 'loose_omega_pieces', 'short_wires', 'missing_anode', 'missing_cathode', 'missing_wires', 'loose_preamp_connections', 'low_anode_cathode_resistances' ]

parser = argparse.ArgumentParser(
                    prog='create_update_qc_panels_table.py',
                    description='Create SQL files for updating qc.panels table',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--panel_id', required=True)
parser.add_argument('--comment', required=True)
for column in all_columns:
    parser.add_argument('--new_'+column, nargs='*', help='Reset the '+column+' column to these straw numbers')
    parser.add_argument('--add_'+column, nargs='*', help='Add these straw numbers to the '+column+' column')
    parser.add_argument('--remove_'+column, nargs='*', help='Remove these straw numbers from the '+column+' column')
parser.add_argument('--earboard', help='True / false whether panel passed ear board test')
parser.add_argument('--hv_test_done', help='True / false whether panel has had HV test done')
parser.add_argument('--passes_amb_dmb_leak_check', help='True / false whether panel passed AMB-DMB leak check')
parser.add_argument('--earflooding_trimming_done', help='True / false whether panel has had earflooding trimming done')
parser.add_argument('--append', type=bool, default=False, help='Append SQL commands to previously created .sql file')

args = parser.parse_args()
dict_args = vars(args) # convert to dictionary

panel_id=args.panel_id
comment=args.comment

all_channels = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95"]

# Check that we don't have new_ defined as well as add_ or removed_
for column in all_columns:
    if (dict_args['new_'+column] != None and (dict_args['add_'+column] != None or dict_args['remove_'+column] != None)):
        print("ERROR: Cannot have both new_"+column+" and add_"+column+" or remove_"+column+" defined.")
        print("new_"+column+": "+', '.join(dict_args['new_'+column]))
        if (dict_args['add_'+column] != None):
            print("add_"+column+": "+', '.join(dict_args['add_'+column]))
        if (dict_args['remove_'+column] != None):
            print("remove_"+column+": "+', '.join(dict_args['remove_'+column]))
        print("Exiting...")
        exit(1)

#print(args.add_missing_straws)
#print(args.remove_missing_straws)

outfilename = '../sql/update_qc_panels_table.sql'#_'+str(panel_id)+'.sql';
print("Creating " + outfilename + " for panel number " + str(panel_id) + "...");

opts='w'
if args.append:
    opts = 'a'
update_sql_file = open(outfilename, opts)
update_sql_file.write("\n\n")
for column in all_columns:
    # if there is any change in this column
    if (dict_args['new_'+column] != None or dict_args['add_'+column] != None or dict_args['remove_'+column] != None):
        # get the old values from qc.panels and create a new row in repairs.panels
        update_sql_file.write("WITH old_values AS (SELECT panel_id,"+column+" from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,"+column+" FROM old_values;\n"); # insert the new repair row with the old values

    # now make the changes to qc.panels
    if (dict_args['remove_'+column] != None):
        if (dict_args['remove_'+column] == 'all'):
            dict_args['remove_'+column] = all_channels
        # Have to remove elements one at a time in psql
        for rem in dict_args['remove_'+column]:
            update_sql_file.write("UPDATE qc.panels SET "+column+"=ARRAY_REMOVE("+column+", "+rem+") where panel_id=" + str(panel_id) + ";\n");

    if (dict_args['new_'+column] != None):
        if (dict_args['new_'+column] == 'all'):
            dict_args['new_'+column] = all_channels
        update_sql_file.write("UPDATE qc.panels SET "+column+"=\'{" + ', '.join(dict_args['new_'+column]) + "}\' where panel_id=" + str(panel_id) + ";\n");

    if (dict_args['add_'+column] != None):
#        print(dict_args['add_'+column])
        if ('all' in dict_args['add_'+column]):
            dict_args['add_'+column] = all_channels
        update_sql_file.write("UPDATE qc.panels SET "+column+"=ARRAY_CAT("+column+", \'{" + ', '.join(dict_args['add_'+column]) + "}\') where panel_id=" + str(panel_id) + ";\n");

    if (dict_args['new_'+column] != None or dict_args['add_'+column] != None or dict_args['remove_'+column] != None):
        # now update repairs table
        update_sql_file.write("UPDATE repairs.panels SET column_changed=\'"+column+"\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
        update_sql_file.write("WITH new_values AS (SELECT panel_id,"+column+" from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT "+column+" FROM new_values) WHERE repair_id=LASTVAL();\n"); # insert the new repair row with the old values


if (dict_args['earboard'] != None):
    update_sql_file.write("WITH old_values AS (SELECT panel_id,earboard from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,earboard FROM old_values;\n"); # insert the new repair row with the old values
    update_sql_file.write("UPDATE qc.panels SET earboard=" + dict_args['earboard'] + " where panel_id=" + str(panel_id) + ";\n");
    update_sql_file.write("UPDATE repairs.panels SET column_changed=\'earboard\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
    update_sql_file.write("WITH new_values AS (SELECT panel_id,earboard from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT earboard FROM new_values) WHERE repair_id=LASTVAL();\n"); # insert the new repair row with the old values

if (dict_args['hv_test_done'] != None):
    update_sql_file.write("WITH old_values AS (SELECT panel_id,hv_test_done from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,hv_test_done FROM old_values;\n"); # insert the new repair row with the old values
    update_sql_file.write("UPDATE qc.panels SET hv_test_done=" + dict_args['hv_test_done'] + " where panel_id=" + str(panel_id) + ";\n");
    update_sql_file.write("UPDATE repairs.panels SET column_changed=\'hv_test_done\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
    update_sql_file.write("WITH new_values AS (SELECT panel_id,hv_test_done from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT hv_test_done FROM new_values) WHERE repair_id=LASTVAL();\n"); # insert the new repair row with the old values


if (dict_args['passes_amb_dmb_leak_check'] != None):
    update_sql_file.write("WITH old_values AS (SELECT panel_id,passes_amb_dmb_leak_check from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,passes_amb_dmb_leak_check FROM old_values;\n"); # insert the new repair row with the old values
    update_sql_file.write("UPDATE qc.panels SET passes_amb_dmb_leak_check=" + dict_args['passes_amb_dmb_leak_check'] + " where panel_id=" + str(panel_id) + ";\n");
    update_sql_file.write("UPDATE repairs.panels SET column_changed=\'passes_amb_dmb_leak_check\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
    update_sql_file.write("WITH new_values AS (SELECT panel_id,passes_amb_dmb_leak_check from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT passes_amb_dmb_leak_check FROM new_values) WHERE repair_id=LASTVAL();\n"); # insert the new repair row with the old values

if (dict_args['earflooding_trimming_done'] != None):
    update_sql_file.write("WITH old_values AS (SELECT panel_id,earflooding_trimming_done from qc.panels WHERE panel_id="+str(panel_id)+") INSERT INTO repairs.panels(panel_id, old_value) SELECT panel_id,earflooding_trimming_done FROM old_values;\n"); # insert the new repair row with the old values
    update_sql_file.write("UPDATE qc.panels SET earflooding_trimming_done=" + dict_args['earflooding_trimming_done'] + " where panel_id=" + str(panel_id) + ";\n");
    update_sql_file.write("UPDATE repairs.panels SET column_changed=\'earflooding_trimming_done\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
    update_sql_file.write("WITH new_values AS (SELECT panel_id,earflooding_trimming_done from qc.panels WHERE panel_id="+str(panel_id)+") UPDATE repairs.panels SET new_value=(SELECT earflooding_trimming_done FROM new_values) WHERE repair_id=LASTVAL();\n"); # insert the new repair row with the old values

print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb08 -p 5459 mu2e_tracker_prd < " + outfilename)
