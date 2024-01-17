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
parser.add_argument('--add_panels_in_order', nargs='*', help='Add panels in order (pos0, pos1, ..., pos5)')
parser.add_argument('--panel_swap_out', nargs=1, help='Swap this panel in')
parser.add_argument('--panel_swap_in', nargs=1, help='Swap this panel out')
parser.add_argument('--panel_swap_pos', nargs=1, help='Position where panel was')
parser.add_argument('--construction_start_date', help='date the plane started construction (format: \'yyyy-mm-dd\')')
parser.add_argument('--construction_end_date', help='date the plane ended construction (format: \'yyyy-mm-dd\')')
parser.add_argument('--append', type=bool, default=False, help='Append SQL commands to previously created .sql file')

args = parser.parse_args()
dict_args = vars(args) # convert to dictionary

plane_id=args.plane_id

panels_to_add=dict_args['add_panels_in_order']
panel_swap_in=dict_args['panel_swap_in']
panel_swap_out=dict_args['panel_swap_out']
panel_swap_pos=dict_args['panel_swap_pos']
#panels_to_remove=dict_args['remove_panels']
construction_start_date=args.construction_start_date
construction_end_date=args.construction_end_date
comment=args.comment

if panels_to_add!=None:
    if (len(panels_to_add) != 6):
        print("ERROR: We want to add all 6 panel_ids at once\n")
        exit(1)
else:
    panels_to_add=[]

if not ((panel_swap_in!=None and panel_swap_out!=None and panel_swap_pos!=None) or (panel_swap_in==None and panel_swap_out==None and panel_swap_pos==None)):
    print("ERROR: All of --panel_swap_in, --panel_swap_out, and --panel_swap_pos are required\n")
    exit(1)

#if panels_to_remove==None:
#    panels_to_remove=[]

# Check that number of added panels = number of removed panels
# if (len(panels_to_add) != len(panels_to_remove)):
#     # Now check if we are adding 6 panels (i.e. adding information for a new plane)

outfilename = '../sql/update_qc_planes_table.sql'#_'+str(plane_id)+'.sql';
print("Creating " + outfilename + " for plane number " + str(plane_id) + "...");

opts='w'
if args.append:
    opts = 'a'

update_sql_file = open(outfilename, opts)


# first get the old values from qc.planes and create a new row in repairs.planes
for pos,add in enumerate(panels_to_add): # want to add panel IDs in order in different columns
#    print(pos,add)
    column="panel_id_pos"+str(pos)
    update_sql_file.write("WITH old_values AS (SELECT plane_id,"+column+" from qc.planes WHERE plane_id="+str(plane_id)+") INSERT INTO repairs.planes(plane_id, old_value) SELECT plane_id,"+column+" FROM old_values;\n"); # insert the new repair row with the old values

    # make changes to qc.planes
    update_sql_file.write("UPDATE qc.planes SET "+column+"="+add+" where plane_id=" + str(plane_id) + ";\n");

    # now update repairs table
    update_sql_file.write("UPDATE repairs.planes SET column_changed=\'"+column+"\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
    update_sql_file.write("WITH new_values AS (SELECT plane_id,"+column+" from qc.planes WHERE plane_id="+str(plane_id)+") UPDATE repairs.planes SET new_value=(SELECT "+column+" FROM new_values) WHERE repair_id=LASTVAL();\n"); # insert the new repair row with the old values

# first get the old values from qc.planes and create a new row in repairs.planes
if (panel_swap_out != None):
    for panel_out,panel_in,panel_pos in zip(panel_swap_out,panel_swap_in,panel_swap_pos): # need to do these together
#        print(panel_out,panel_in,panel_pos)

        column="panel_id_pos"+str(panel_pos)
        update_sql_file.write("WITH old_values AS (SELECT plane_id,"+column+" from qc.planes WHERE plane_id="+str(plane_id)+") INSERT INTO repairs.planes(plane_id, old_value) SELECT plane_id,"+column+" FROM old_values;\n"); # insert the new repair row with the old values

        # make changes to qc.planes
        update_sql_file.write("UPDATE qc.planes SET "+column+"="+panel_in+" where plane_id=" + str(plane_id) + ";\n");

        # now update repairs table
        update_sql_file.write("UPDATE repairs.planes SET column_changed=\'"+column+"\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
        update_sql_file.write("WITH new_values AS (SELECT plane_id,"+column+" from qc.planes WHERE plane_id="+str(plane_id)+") UPDATE repairs.planes SET new_value=(SELECT "+column+" FROM new_values) WHERE repair_id=LASTVAL();\n"); # insert the new repair row with the old values


if (construction_start_date != None):
    update_sql_file.write("WITH old_values AS (SELECT plane_id,construction_start_date from qc.planes WHERE plane_id="+str(plane_id)+") INSERT INTO repairs.planes(plane_id, old_value) SELECT plane_id,construction_start_date FROM old_values;\n"); # insert the new repair row with the old values
    # make changes to qc.planes
    update_sql_file.write("UPDATE qc.planes SET construction_start_date=\'"+construction_start_date+"\' where plane_id=" + str(plane_id) + ";\n");
    # now update repairs table
    update_sql_file.write("UPDATE repairs.planes SET column_changed=\'construction_start_date\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
    update_sql_file.write("WITH new_values AS (SELECT plane_id,construction_start_date from qc.planes WHERE plane_id="+str(plane_id)+") UPDATE repairs.planes SET new_value=(SELECT construction_start_date FROM new_values) WHERE repair_id=LASTVAL();\n"); # insert the new repair row with the old values

if (construction_end_date != None):
    update_sql_file.write("WITH old_values AS (SELECT plane_id,construction_end_date from qc.planes WHERE plane_id="+str(plane_id)+") INSERT INTO repairs.planes(plane_id, old_value) SELECT plane_id,construction_end_date FROM old_values;\n"); # insert the new repair row with the old values
    # make changes to qc.planes
    update_sql_file.write("UPDATE qc.planes SET construction_end_date=\'"+construction_end_date+"\' where plane_id=" + str(plane_id) + ";\n");
    # now update repairs table
    update_sql_file.write("UPDATE repairs.planes SET column_changed=\'construction_end_date\',date_uploaded=\'"+date.today().strftime('%Y-%m-%d')+"\',comment=\'"+comment+"\' where repair_id=LASTVAL();\n") # now add the changed column and comment
    update_sql_file.write("WITH new_values AS (SELECT plane_id,construction_end_date from qc.planes WHERE plane_id="+str(plane_id)+") UPDATE repairs.planes SET new_value=(SELECT construction_end_date FROM new_values) WHERE repair_id=LASTVAL();\n"); # insert the new repair row with the old values



print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb08 -p 5459 mu2e_tracker_prd < " + outfilename)
