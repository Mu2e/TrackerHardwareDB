import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def replace_problem_chars(string):
    return string.replace('[', '').replace(']', '').replace('\'', '').replace('\"', '')#.replace('\\n', '')

cols_to_extract = {'Missing_straws': 'missing_straws',
                   'Missing_wires': 'missing_wires',
                   'High_currents' : 'high_current_wires',
                   'Blocked_straws' : 'blocked_straws',
                   'Sparks' : 'sparking_wires',
                   'Brooken_wires' : 'broken_wires',
#                   'Loose_anode_pin' : # no column in db for this
#                   'Loose_cathode_pins' : # no column in db for this
                   'Loose_omegas' : 'loose_omega_pieces',
                   'Missing_anode_pins' : 'missing_anode',
                   'Missing_cathode_pins' : 'missing_cathode',
                   'Missing_omegas' : 'missing_omegas'}

min_panel_id=1
max_panel_id=300

outfilename = 'run_create_update_qc_panels_table.sh';
create_sh_file = open(outfilename, 'w')
for panel_id in np.linspace(min_panel_id, max_panel_id, num=max_panel_id,dtype=int):
    df = pd.read_csv('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=imported.fnal_planes&w=panel_id:eq:'+str(panel_id))
    df_prev = pd.read_csv('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=imported.fnal_planes_previous&w=panel_id:eq:'+str(panel_id))

    joined_df = pd.merge(df, df_prev, left_on=['panel_id', 'file_name'], right_on=['panel_id', 'file_name'], suffixes=["_current", "_previous"])

    joined_df['last_modified_current'] = pd.to_datetime(joined_df['last_modified_current'], format='%Y-%m-%d %H:%M:%S')
    joined_df['last_modified_previous'] = pd.to_datetime(joined_df['last_modified_previous'], format='%Y-%m-%d %H:%M:%S')
    joined_df = joined_df.loc[(joined_df['last_modified_current'] - joined_df['last_modified_previous'])>timedelta(hours=1)]; #  need to ignore anything with a 1 hour time difference because that is just from time change (not sure why that happens...)


    if (len(joined_df)==0):
        print("Panel ID "+str(panel_id)+": no changes since last import")
    # Only write an update command if there are any changes
    else:
        print("\nPanel ID "+str(panel_id)+":")
        print("Changes since last import:")
        print(joined_df[['file_name', 'file_contents_previous', 'file_contents_current']])
        print("\n")

        # Updates for qc.panels
        command = "python3 create_update_qc_panels_table.py --panel_id "+str(panel_id);
        commands_added = False
        for col in cols_to_extract:
            if (len(joined_df.loc[(joined_df['file_name']==col)])>0):
                old_vals = replace_problem_chars(str(joined_df.loc[(joined_df['file_name'] == col)][['file_contents_previous']].values))
                old_vals_str_array = old_vals.split(',')
                old_vals_int_array=[]

                new_vals = replace_problem_chars(str(joined_df.loc[(joined_df['file_name'] == col)][['file_contents_current']].values))
                new_vals_str_array = new_vals.split(',')
                new_vals_int_array=[]

                # go through both old and new vals and check that we get integers for all of these
                for val_str_array, val_int_array in zip([old_vals_str_array, new_vals_str_array], [old_vals_int_array, new_vals_int_array]):
                    for str_val in val_str_array:
                        if str_val == "":
                            continue

                        try:
                            val_int_array.append(int(str_val))
                        except ValueError:
                            print("!!! \"" + str_val + "\" from file "+col+" did not automatically convert to an integer.")
                            print("The full string we are trying to parse is: \""+', '.join(val_str_array)+"\"")
                            user_vals = input("Please input the correct values for \""+str_val+"\" (comma separated): ").split(',')
#                            print(user_vals)
                            for user_val in user_vals:
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

                if (len(vals_to_remove)>0):
                    commands_added=True
                    command = command +" --remove_" + cols_to_extract[col] + " "+' '.join(vals_to_remove)

                if (len(vals_to_add)>0):
                    commands_added=True
                    command = command +" --add_" + cols_to_extract[col] + " "+' '.join(vals_to_add)

        if commands_added:
            create_sh_file.write(command+"\n")
        else:
            print("Panel ID "+str(panel_id)+": nothing to change in DB")
