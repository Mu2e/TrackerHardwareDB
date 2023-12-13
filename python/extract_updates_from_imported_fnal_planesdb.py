import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os
import argparse

def replace_problem_chars(string):
    return string.replace('[', '').replace(']', '').replace('\'', '').replace('\"', '')#.replace('\\n', '')


parser = argparse.ArgumentParser(
                    prog='extract_updates_from_imported_fnal_planes_db.py',
                    description='Extracting data from imported.fnal_planes_db to create bash script to update qc.panels and qc.planes tables',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')
parser.add_argument('--snapshot_date', required=True)
parser.add_argument('--min_panel_id', type=int, default=1)

args = parser.parse_args()
snapshot_date = args.snapshot_date

cols_to_extract = {'Missing_straws': 'missing_straws',
                   'Missing_wires': 'missing_wires',
                   'High_currents' : 'high_current_wires',
                   'Blocked_straws' : 'blocked_straws',
                   'Sparks' : 'sparking_wires',
                   'Brooken_wires' : 'broken_wires',
#                   'Loose_anode_pin' : # no column in db for this
#                   'Loose_cathode_pins' : # no column in db for this
#                   'Loose_omegas' : 'missing_omega_pieces', # loose omega piaces are now the same as missing omega pieces
                   'Missing_anode_pins' : 'missing_anode',
                   'Missing_cathode_pins' : 'missing_cathode',
                   'Missing_omegas' : 'missing_omega_pieces',
                   'Shorts' : 'short_wires',
                   'Plane_number' : 'tbd'}

cols_to_check = [ 'Loose_omega', 'Notes', 'HV_issues', 'HV_test_done', 'Repairs', 'Air_test_for_blocked_straws' ] # move Loose_omega to just a thing we should check

min_panel_id=args.min_panel_id
max_panel_id=300

outfilename = 'run_create_update_qc_panels_table.sh';
create_sh_file = open(outfilename, 'w')

for panel_id in np.linspace(min_panel_id, max_panel_id, num=(max_panel_id-min_panel_id)+1,dtype=int):
    to_add_to_planes={}
    to_remove_from_planes={}
    df = pd.read_csv('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=imported.fnal_planes&w=panel_id:eq:'+str(panel_id))
    df_prev = pd.read_csv('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=imported.fnal_planes_previous&w=panel_id:eq:'+str(panel_id))

    joined_df = pd.merge(df, df_prev, how='left', left_on=['panel_id', 'file_name'], right_on=['panel_id', 'file_name'], suffixes=["_current", "_previous"])

    joined_df['last_modified_current'] = pd.to_datetime(joined_df['last_modified_current'], format='%Y-%m-%d %H:%M:%S')
    joined_df['last_modified_previous'] = pd.to_datetime(joined_df['last_modified_previous'], format='%Y-%m-%d %H:%M:%S')
    joined_df = joined_df.loc[((joined_df['last_modified_current'] - joined_df['last_modified_previous'])>timedelta(hours=1)) | (joined_df['last_modified_previous'].isna())]; #  need to ignore anything with a 1 hour time difference because that is just from time change (not sure why that happens..), or that 
    joined_df = joined_df.loc[(joined_df['file_contents_current'] != "\"\"")]


#    print(df_prev.loc[df_prev['panel_id']==263])
#    print(df.loc[df['panel_id']==263])

    if (len(joined_df)==0):
        print("Panel ID "+str(panel_id)+": no changes since last import")
    # Only write an update command if there are any changes
    else:
        print("\nPanel ID "+str(panel_id)+":")
        print("===========")
        print("Changes since last import: ")
        print(joined_df[['file_name', 'file_contents_previous', 'file_contents_current']])
        print("\n")

        # Updates for qc.panels
        base_panel_command = "python3 create_update_qc_panels_table.py --panel_id "+str(panel_id) + " --append true";
        panel_commands=[]
        panel_commands_added = False

        base_plane_command = "python3 create_update_qc_planes_table.py --append true"
        plane_commands_added = False
        print("\nExtracting lists of integers from FNAL Plane DB files that should contain them...")
        for col in cols_to_extract:
            if (len(joined_df.loc[(joined_df['file_name']==col)])>0):
                old_vals = replace_problem_chars(str(joined_df.loc[(joined_df['file_name'] == col)][['file_contents_previous']].values))
                old_vals_str_array = old_vals.split(',')
                old_vals_int_array=[]

                new_vals = replace_problem_chars(str(joined_df.loc[(joined_df['file_name'] == col)][['file_contents_current']].values))
                new_vals_str_array = new_vals.split(',')
                new_vals_int_array=[]

                if old_vals == new_vals:
                    continue

                # go through both old and new vals and check that we get integers for all of these
                for val_str_array, val_int_array in zip([old_vals_str_array, new_vals_str_array], [old_vals_int_array, new_vals_int_array]):
                    for str_val in val_str_array:
                        if str_val == "" or str_val=="removed" or str_val=="none" or str_val=="nan": # "removed" and "none" are used for plane numbers, "nan" is when the panel didn't exist before
                            continue

                        try:
                            val_int_array.append(int(str_val))
                        except ValueError:
                            print("!!! Parse error from file \""+col+"\":") #\"" + str_val + "\" from file "+col+" did not automatically convert to an integer.")
                            print("\t The full file contents is \""+', '.join(val_str_array)+"\"")
                            print("\t The parsing error is here: \"" + str_val + "\"")
                            user_vals = input("What should the correct values be? (if multiple values, separate them by commas; if no value needed, press enter): ").split(',')
#                            print(user_vals)
                            for user_val in user_vals:
                                if user_val == "":
                                    continue
                                try:
                                    val_int_array.append(int(user_val))
                                except ValueError:
                                    print("ERROR: Did not input an integer. Exiting...")
                                    exit(1)

#                print(old_vals_int_array)
#                print(new_vals_int_array)

                # Now work out which values need to be removed and which need to be added
                vals_to_remove=[]
                vals_to_add=[]
                for old_val in old_vals_int_array:
                    if old_val not in new_vals_int_array:
                        vals_to_remove.append(str(old_val))

                for new_val in new_vals_int_array:
                    if new_val not in old_vals_int_array:
                        vals_to_add.append(str(new_val))

                if (col != 'Plane_number'):
                    if (len(vals_to_remove)>0):
                        default_comment = "from "+col+" file of FNAL Planes DB snapshot of "+snapshot_date
                        comment = input("Removing "+", ".join(vals_to_remove)+". Add comment for this change (default: \""+default_comment+"\": ")
                        if comment == "":
                            comment = default_comment
                        panel_command = base_panel_command +" --remove_" + cols_to_extract[col] + " "+' '.join(vals_to_remove) + " --comment \"" + comment + "\""
                        panel_commands.append(panel_command)

                    if (len(vals_to_add)>0):
                        default_comment = "from "+col+" file of FNAL Planes DB snapshot of "+snapshot_date
                        comment = input("Adding "+", ".join(vals_to_add)+". Add comment for this change (default: \""+default_comment+"\"): ")
                        if comment == "":
                            comment = default_comment
                        panel_command = base_panel_command +" --add_" + cols_to_extract[col] + " "+' '.join(vals_to_add) + " --comment \"" + comment + "\""
                        panel_commands.append(panel_command)
                else:
                    if (len(vals_to_remove)>0):
                        for plane_id in vals_to_remove:
                            if int(plane_id) not in to_remove_from_planes.keys():
                                to_remove_from_planes[int(plane_id)] = []
                            to_remove_from_planes[int(plane_id)].append(panel_id)
                        plane_commands_added=True

                    if (len(vals_to_add)>0):
                        for plane_id in vals_to_add:
                            if int(plane_id) not in to_add_to_planes.keys():
                                to_add_to_planes[int(plane_id)] = []
                            to_add_to_planes[int(plane_id)].append(panel_id)
                        plane_commands_added=True

        if (len(panel_commands)>0):
            print("\nAt the moment, we will be running these panel commands:")
            for panel_command in panel_commands:
                print("  \""+panel_command+"\"\n")

        print("Now checking other files where we may need to get some extra information:")
        for col in cols_to_check:
            if (len(joined_df.loc[(joined_df['file_name']==col)])>0):
                old_vals = replace_problem_chars(str(joined_df.loc[(joined_df['file_name'] == col)][['file_contents_previous']].values))
                new_vals = replace_problem_chars(str(joined_df.loc[(joined_df['file_name'] == col)][['file_contents_current']].values))
#                print(old_vals)
#                print(new_vals)
                diff = list(set(new_vals.split('\\n')) - set(old_vals.split('\\n'))) # want to ignore newline differences
                print("New contents in file \""+col+"\":")
                print("\t\""+", ".join(diff)+"\"");
                user_additions = input("Enter extra arguments (leave empty if none required): ")
                if user_additions != "":
                    default_comment = "from "+col+" file of FNAL Planes DB snapshot of "+snapshot_date
                    comment = input("Add comment for this change (default: \""+default_comment+"\"): ")
                    if comment == "":
                        comment = default_comment
                    panel_command = base_panel_command + " " + user_additions + " --comment \"" + comment + "\""
                    panel_commands.append(panel_command)

        if (len(panel_commands)>0):
            for panel_command in panel_commands:
                create_sh_file.write(panel_command+"\n")
        if plane_commands_added:
            print("Panel ID "+str(panel_id)+": changed planes")
            for plane_id in np.linspace(0, 40, 41, dtype=int):
                if (plane_id in to_remove_from_planes.keys() or plane_id in to_add_to_planes.keys()):
                    plane_command = base_plane_command + " --plane_id " + str(plane_id);

                    if (plane_id in to_remove_from_planes.keys()):
                        plane_command = plane_command + " --remove_panels "
                        for panel_id in to_remove_from_planes[plane_id]:
                            plane_command = plane_command + " " + str(panel_id)

                    if (plane_id in to_add_to_planes.keys()):
                        plane_command = plane_command + " --add_panels ";
                        for panel_id in to_add_to_planes[plane_id]:
                            plane_command = plane_command + " " + str(panel_id)

                    default_comment = "from Plane_number file of FNAL Planes DB snapshot of "+snapshot_date
                    create_sh_file.write(plane_command+" --comment \""+default_comment+"\"\n")

        if not plane_commands_added and len(panel_commands)==0:
            print("Panel ID "+str(panel_id)+": nothing to change in DB")

#print(to_remove_from_planes)
#print(to_add_to_planes)
