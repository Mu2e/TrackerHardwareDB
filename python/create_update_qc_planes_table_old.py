import os
import argparse

import time
import numpy as np
import pandas as pd
from datetime import date

parser = argparse.ArgumentParser(
                    prog='create_update_qc_planes_table.py',
                    description='Create SQL files for updating qc.planes table',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--plane_id', required=True)
parser.add_argument('--comment', required=True)
parser.add_argument('--add_panels', nargs='*', help='Add these panels')
parser.add_argument('--remove_panels', nargs='*', help='Remove these panels')
parser.add_argument('--append', type=bool, default=False, help='Append SQL commands to previously created .sql file')

args = parser.parse_args()
dict_args = vars(args) # convert to dictionary

plane_id=args.plane_id

panels_to_add=dict_args['add_panels']
panels_to_remove=dict_args['remove_panels']
comment=args.comment

if panels_to_add==None:
    panels_to_add=[]
if panels_to_remove==None:
    panels_to_remove=[]

# Check that number of added panels = number of removed panels
# if (len(panels_to_add) != len(panels_to_remove)):
#     # Now check if we are adding 6 panels (i.e. adding information for a new plane)
#     if (len(panels_to_add) != 6):
#         print("ERROR: Expected either (a) number of panels to add = number of panels to remove, or (b) number of panels to add = 6. Exiting...");
#         exit(1)

outfilename = '../sql/update_qc_planes_table.sql'#_'+str(plane_id)+'.sql';
print("Creating " + outfilename + " for plane number " + str(plane_id) + "...");

opts='w'
if args.append:
    opts = 'a'

update_sql_file = open(outfilename, 'a')

# first get the old values from qc.planes and create a new row in repairs.planes
update_sql_file.write("WITH old_values AS (SELECT plane_id,panel_ids from qc.planes WHERE plane_id="+str(plane_id)+") INSERT INTO repairs.planes(plane_id, old_value) SELECT plane_id,panel_ids FROM old_values;\n"); # insert the new repair row with the old values

# make changes to qc.planes
update_sql_file.write("UPDATE qc.planes SET panel_ids=ARRAY_CAT(panel_ids, \'{" + ', '.join(panels_to_add) + "}\') where plane_id=" + str(plane_id) + ";\n");
for rem in panels_to_remove: # have to remove elements one at a time in psql
    update_sql_file.write("UPDATE qc.planes SET panel_ids=ARRAY_REMOVE(panel_ids, "+rem+") where plane_id=" + str(plane_id) + ";\n");

# now update repairs table
update_sql_file.write("UPDATE repairs.planes SET column_changed=\'plane_ids\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
update_sql_file.write("WITH new_values AS (SELECT plane_id,panel_ids from qc.planes WHERE plane_id="+str(plane_id)+") UPDATE repairs.planes SET new_value=(SELECT panel_ids FROM new_values) WHERE repair_id=LASTVAL();\n"); # insert the new repair row with the old values


print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb11 -p 5459 mu2e_tracker_prd < " + outfilename)
