import os
import argparse

import time
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(
                    prog='create_insert_new_panels.py',
                    description='Create SQL files for inserting new panels into the qc.panels table',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--panel_ids', required=True, nargs='*')

args = parser.parse_args()

panel_ids=args.panel_ids

outfilename = '../sql/insert_new_panels.sql';
print("Creating " + outfilename + " for panel ids [" + ', '.join(panel_ids) + "]...");

insert_sql_file = open(outfilename, 'w')
for panel_id in panel_ids:
    insert_sql_file.write("INSERT INTO qc.panels(id) VALUES(" + str(panel_id) + ");\n");

print("Done!");
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb08 -p 5459 mu2e_tracker_prd < " + outfilename)
