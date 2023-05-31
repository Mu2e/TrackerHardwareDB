import os
import argparse

import time
import numpy as np
import pandas as pd

all_columns=['missing_straws', 'high_current_wires', 'blocked_straws', 'sparking_wires', 'no_hv_straw_hv', 'no_hv_straw_cal', 'missing_omega_pieces', 'loose_omega_pieces', 'short_wires', 'missing_anode', 'missing_cathode', 'low_flow_straws', 'missing_wires' ]

parser = argparse.ArgumentParser(
                    prog='create_update_qc_panels_table.py',
                    description='Create SQL files for updating qc.panels table',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--panel_id', required=True)
for column in all_columns:
    parser.add_argument('--new_'+column, nargs='*', help='Reset the '+column+' column to these straw numbers')
    parser.add_argument('--add_'+column, nargs='*', help='Add these straw numbers to the '+column+' column')
    parser.add_argument('--remove_'+column, nargs='*', help='Remove these straw numbers from the '+column+' column')

args = parser.parse_args()
dict_args = vars(args) # convert to dictionary

panel_id=args.panel_id

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

outfilename = '../sql/update_qc_panels_table.sql';
print("Creating " + outfilename + " for panel number " + str(panel_id) + "...");

update_sql_file = open(outfilename, 'w')
for column in all_columns:
    if (dict_args['new_'+column] != None):
        update_sql_file.write("UPDATE qc.panels SET "+column+"=\'{" + ', '.join(dict_args['new_'+column]) + "}\' where id=" + str(panel_id) + ";\n");

    if (dict_args['add_'+column] != None):
        update_sql_file.write("UPDATE qc.panels SET "+column+"=ARRAY_CAT("+column+", \'{" + ', '.join(dict_args['add_'+column]) + "}\' where id=" + str(panel_id) + ";\n");

    if (dict_args['remove_'+column] != None):
        # Have to remove elements one at a time in psql
        for rem in dict_args['remove_'+column]:
            update_sql_file.write("UPDATE qc.panels SET "+column+"=ARRAY_REMOVE("+column+", "+rem+") where id=" + str(panel_id) + ";\n");

print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb08 -p 5459 mu2e_tracker_prd < " + outfilename)
