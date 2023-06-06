import os
import argparse

import time
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(
                    prog='create_update_qc_planes_table.py',
                    description='Create SQL files for updating qc.planes table',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--plane_id', required=True)
parser.add_argument('--add_panels', nargs='*', help='Add these panels')
parser.add_argument('--remove_panels', nargs='*', help='Remove these panels')

args = parser.parse_args()
dict_args = vars(args) # convert to dictionary

plane_id=args.plane_id


outfilename = '../sql/update_qc_planes_table.sql';
print("Creating " + outfilename + " for plane number " + str(plane_id) + "...");

update_sql_file = open(outfilename, 'w')
if (dict_args['add_panels'] != None):
    update_sql_file.write("UPDATE qc.planes SET panels=ARRAY_CAT(panel_ids, \'{" + ', '.join(dict_args['add_panels']) + "}\') where plane_id=" + str(plane_id) + ";\n");
if (dict_args['remove_panels'] != None):
    # Have to remove elements one at a time in psql
    for rem in dict_args['remove_panels']:
        update_sql_file.write("UPDATE qc.planes SET panel_ids=ARRAY_REMOVE(panel_ids, "+rem+") where plane_id=" + str(plane_id) + ";\n");


print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb08 -p 5459 mu2e_tracker_prd < " + outfilename)
