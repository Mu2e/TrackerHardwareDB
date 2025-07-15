import os
import argparse
import mimetypes

from datetime import date

from qc_panels_columns import single_ch_issues
from qc_panels_columns import single_panel_tests

def check_filename(filename):
    return filename[:2] == "MN" and filename[-13:] == "_Traveler.pdf" and len(filename) == 18

parser = argparse.ArgumentParser(
                    prog='add_travelers.py',
                    description='Add traveler images to the repository and update the database',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('--traveler_dir', required=True, help='Directory where the travelers are')
parser.add_argument('--never_replace', action='store_true', help='Don\'t ask to replace a file', default=False)

args = parser.parse_args()
dict_args = vars(args) # convert to dictionary
never_replace = args.never_replace

# We will write a bash script that will handle a bunch of things
# For the time being, hold in to what we want to write to a file but don't do it yet, in case we decide against it
write_to_file=True
# Create the script
bash_script_name = 'add_travelers.sh'
bash_script = open(bash_script_name, 'w')
bash_script.write('#!/bin/bash\n')
bash_script.write("rm ../sql/update_qc_panels_table.sql\n")

traveler_dir = args.traveler_dir
for root, dirs, files in os.walk(traveler_dir):
    for filename in files:
        write_to_file = True
        bash_commands=""
        traveler_img=root+"/"+filename

        # Check that the file type is correct (PDF)
        # If it isn't, then try to convert it
        # If we can't convert it, then throw an error and exit
        skip = False
        mimetype, encoding = mimetypes.guess_type(traveler_img)
        if mimetype:
            if mimetype != "application/pdf":
                if mimetype == "image/jpeg":
                    bash_commands = bash_commands + "convert \'"+traveler_img+"\'";
                    suffix = traveler_img.split('.')[-1]
                    traveler_img = traveler_img.replace("."+suffix, ".pdf")
                    bash_commands = bash_commands + " \'"+traveler_img+"\'\n";
                else:
                    print(f"ERROR: this script does not support {mimetype} filetype")
                    skip = True
        else:
            print("Could not determine MIME type.")
        if skip:
            print("Skipping "+traveler_img)
            continue # to next panel

        # Now make sure that the file is named correctly
        # If it isn't, ask the user to rename it and add a mv command to the bashscript
        filename = traveler_img.split('/')[-1]
        filename_ok = check_filename(filename)
        while (filename_ok == False):
            old_filename = filename
            panel_number = input("Filename "+filename+" doesn't follow convention \"MN###_Traveler.pdf\". Please enter panel number (s=skip): ")
            if panel_number in ['s', 'S']:
                skip = True
                break
            panel_number = panel_number.rjust(3, '0')
            filename = "MN" + panel_number + "_Traveler.pdf"
            filename_ok = check_filename(filename)
            if (filename_ok):
                bash_commands = bash_commands + "mv \'"+traveler_img+"\'";
                traveler_img = traveler_img.replace(old_filename, filename)
                bash_commands = bash_commands + " \'"+traveler_img+"\'\n";
            #    print(filename, filename_ok)
        if skip:
            print("Skipping "+traveler_img)
            continue # to next panel

        # Check whether the traveler_img is already in the panel-qc-viewer/public/images/travelers folder
        # If it isn't, then move it to the correct place
        dirname = '/'.join(traveler_img.split('/')[:-1]) # get just the directory and not the file name
        correct_dir = "../panel-qc-viewer/public/images/travelers"
        if dirname != correct_dir:
            # Check if the file already exists in the panel-qc-viewer/public/images/travelers/ folder
            correct_traveler_img = traveler_img.replace(dirname, correct_dir)
            move_file = False
            if os.path.exists(correct_traveler_img):
                replace = ""
                if never_replace:
                    replace = 'n'

                while replace not in ['y', 'Y', 'n', 'N']:
                    replace = input(traveler_img + " already exists. Replace (y/n): ");
                if replace in ['y', 'Y']:
                    move_file = True
                else:
                    move_file = False
                    write_to_file = False
            else:
                # safe to move
                move_file = True
        if move_file:
            bash_commands = bash_commands + "cp \'"+traveler_img+"\'"
            traveler_img = traveler_img.replace(dirname, correct_dir)
            bash_commands = bash_commands + " \'"+traveler_img+"\'\n"
            bash_commands = bash_commands + "git add \'" + traveler_img +"\'\n"



        try:
            panel_id=int(filename[2:5])
        except ValueError:
            print("ERROR: "+filename[2:5]+" could not be converted to a panel_id")
            exit(1)

        if write_to_file:
            print("Adding "+traveler_img+"...")
            bash_script.write(bash_commands);
            # commit the images
            bash_script.write("python3 create_update_qc_panels_table.py --append=True --panel_id " + str(panel_id) + " --have_traveler true --comment \'adding traveler\'\n");


# Want to do this after going through all travelers
bash_script.write("git commit -m \"adding travelers\"")
bash_script.write("git push")


print("Done!")
print("Now check " + bash_script_name + " looks OK and run it like this:")
print(" . ./" + bash_script_name);
