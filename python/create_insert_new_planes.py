import os
import argparse

import time
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(
                    prog='create_insert_new_planes.py',
                    description='Create SQL files for inserting new planes into the qc.planes table',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--plane_ids', required=True, nargs='*')

args = parser.parse_args()

plane_ids=args.plane_ids

outfilename = '../sql/insert_new_planes.sql';
print("Creating " + outfilename + " for plane ids [" + ', '.join(plane_ids) + "]...");

insert_sql_file = open(outfilename, 'w')
for plane_id in plane_ids:
    insert_sql_file.write("INSERT INTO qc.planes(plane_id) VALUES(" + str(plane_id) + ");\n");

print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb08 -p 5459 mu2e_tracker_prd < " + outfilename)
