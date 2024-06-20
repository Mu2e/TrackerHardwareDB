import re # regexp
import os
import argparse
import tarfile

from datetime import date, datetime
from collections import deque
import time
import numpy as np
import pandas as pd

def get_panel_id(string):
    return string.replace('mn', '').replace('MN', '').replace('test', '').replace('currvstime_', '');

def get_filename(string):
    return string.split('/')[-1]

def add_escape_chars(string):
    return string.replace('\'', '\'\'')

parser = argparse.ArgumentParser(
                    prog='create_insert_panel_hv_data_files.py',
                    description='Create SQL files for tarring raw panel HV data and inserting file information into the database',
                    epilog='For help contact Andy Edmonds via e-mail/Slack')

parser.add_argument('directories', nargs='+', help='Directories with CSV and README files to upload')

args = parser.parse_args()

basedirs=args.directories
for basedir in basedirs:
    if (not os.path.exists(basedir)):
        print("Directory \"" + basedir + "\" does not exist");
        exit(1);


readme_filenames=[]
csv_filenames=[]
dat_filenames=[]
log_filenames=[]
input_filenames=[]
for basedir in basedirs:
    with os.scandir(basedir) as all_files:
        for i_file in all_files:
            if (i_file.is_file()):
                if (".swp" in i_file.name): # some system files
                    continue;
                if ("sweep" in i_file.name): # ignore sweep.log
                    continue;
                if("README" in i_file.name):
                    readme_filenames.append(basedir+i_file.name)
                if(".csv" in i_file.name and "~" not in i_file.name):
                    csv_filenames.append(basedir+i_file.name)
                if(".dat" in i_file.name): # we changed to .dat files at some point, include them in the tarballs
                    csv_filenames.append(basedir+i_file.name)
                if(".log" in i_file.name): # with the change .dat, we also added log files and input files so keep those too
                    log_filenames.append(basedir+i_file.name)
                if("input" in i_file.name): # with the change .dat, we also added log files and input files so keep those too
                    input_filenames.append(basedir+i_file.name)

#print("README files:\n"+'\n'.join(readme_filenames))
#print("CSV files:\n"+'\n'.join(csv_filenames))

# clean up lines in README files
readme_dict={}
input_dict={} # keep track of the input file for each .dat file
log_dict={} # keep track of the log file for each .dat file
counter=0
last_name=""
for readme_filename in readme_filenames:
    readme_file = open(readme_filename, 'r')
    for line in readme_file:
        if "--" in line or "##" in line: # this is a line that looks like a heading
            continue
        if (":" not in line and "mn" in line): # the ":" is missing so insert one close to where it should be
            mn_pos = line.find("mn")
            space_pos = line.find(" ", mn_pos) # first space after "mn"
            prev_line=line
            line = prev_line[:space_pos] + ": " + prev_line[space_pos:]

        words = line.split(":"); # this will split the line into "mnXXX" and "comment"
        # make initial extraction of panel_id and comment
        initial_name = words[0]
        comment = line.replace(initial_name,'')

        # clean up initial_name string
        initial_name = initial_name.replace('-', '')
        initial_name = initial_name.replace(' ', '')
        initial_name = initial_name.replace('\n', '')

        # check for multiple names in the line
        names = initial_name.split(',')
        if "{" in initial_name: # sometimes we have strings like "mn135_{2..6}" or "mn096_{2,3,4}"
            base_name=initial_name.split('{')[0]
            num_range=initial_name.split('{')[1].replace('}', '')
#            print(initial_name)
#            print(num_range)
            min_num=0
            max_num=0
            nums=[]
            if (".." in num_range and ',' not in num_range):
                min_num = int(num_range.split('..')[0])
                max_num = num_range.split('..')[1]
                if (max_num == ""): # an open ended range e.g. "mn161_{6..}"
                    max_num = 100 #  pick a large number
                else:
                    max_num = int(max_num)
                nums=range(min_num, max_num+1)
            elif ("," in num_range and ".." not in num_range):
                nums = num_range.split(',')
            elif ("," in num_range and ".." in num_range):
                initial_nums=num_range.split(',')
#                print(initial_nums)
                for num in initial_nums:
                    if ('..' in num):
                        min_num = int(num.split('..')[0])
                        max_num = num.split('..')[1]
                        if (max_num == ""): # an open ended range e.g. "mn161_{6..}"
                            max_num = 100 #  pick a large number
                        else:
                            max_num = int(max_num)
                        for i_num in range(min_num, max_num+1):
                            nums.append(i_num)
                    else:
                        nums.append(num)

#            print(nums)
            names=[]
            # insert any missing numbers
            for i_num in nums:
                names.append(base_name+str(i_num))
#            print(names)

        # Now check for bare ".." elements
        for i,name in enumerate(names):
            if name == "..":
                if (i != len(names)-1):
                    min_num = int(names[i-1].split("_")[-1])
                    max_num = int(names[i+1].split("_")[-1])
                    for i_num in range(min_num, max_num+1):
                        names.append(str(i_num))
                names[i] = ""; # clear the ".."


        # make sure each name has a panel number etc
        for i_name,name in enumerate(names):
            if name == "..": # sometimes we have stray ".."
                continue
            if "mn" not in name:
                if len(names)>1 and i_name!=0:
                    basename=''.join(names[0].split("_")[:-1]) # chop off last bit of the first name
                    names[i_name] = basename;
                    if ("_" not in name):
                        names[i_name] += "_";
                    names[i_name] += name;
                else: # assume that it's a comment that should have be appended to the previous entry
                    if last_name != "": # if there is no last_name, then we are at the beginning of the file
                        readme_dict[last_name] += "; " + line.replace('\n','')
                    names=[]
                    break # in case the comment line had a comma in it and so len(names)>1 -- we don't want to add the same line twice

        # clean up comment
        comment = comment.replace('\n', '')
        comment = comment.replace(': ', '', 1)

        # in the comment we need to look for the corresponding input and log file names
        for input_filename in input_filenames:
            if input_filename.split('/')[-1] in comment:
                for name in names:
                    input_dict[name] = input_filename

        for log_filename in log_filenames:
            if log_filename.split('/')[-1] in comment:
                for name in names:
                    log_dict[name] = log_filename

        comment = add_escape_chars(comment)

        for name in names: # there could be more than one file referred to in each line of the README
            readme_dict[name] = comment;
            last_name = name

#        if counter > 300:
#            break
        counter=counter+1

#print(readme_dict.keys())
#print(input_dict)
#print(log_dict)

# print("\nMap of csv file name to README comment:")
# counter=0
# for name in readme_dict:
#     if (counter<5):
#         print(name+" -> "+readme_dict[name])
#     if counter == 5:
#         print("...")
#     elif counter > (len(readme_dict)-5):
#         print(name+" -> "+readme_dict[name])
#     counter=counter+1


outfilename = '../sql/insert_panel_hv_data_files.sql';
print("\nCreating " + outfilename + "...")
insert_sql_file = open(outfilename, 'w')

insert_sql_file.write("INSERT INTO qc.panel_hv_data_files(panel_id, filename, first_timestamp, last_timestamp, tarball, comment) VALUES ");

# Now go through and work out which csv files will go into a tarfile
tarfile_dict={}
print("\nDeciding which csv, dat, input, and log files to put in which tarball (this can take a while...)")
n_csv_files=len(csv_filenames)
counter=-1
for i_csv_filename in csv_filenames:
    counter = counter+1
    if (counter % 100 == 0):
        print(str(counter)+" / "+str(n_csv_files)+" processed")

    panel_id=''
    comment=''
    found=False
    i_csv_filename_mod = get_filename(i_csv_filename)
#    print(i_csv_filename+" --> "+i_csv_filename_mod)
    if i_csv_filename_mod == "":
        continue

    tarname = i_csv_filename_mod.split("_")[0]
    tarname_found=False
    if ("mn" not in tarname) and ("MN" not in tarname):
        tarname="_".join(i_csv_filename_mod.split("_")[1:]).split("_")[0] # could have "currvstime" at start
        if ("mn" not in tarname) and ("MN" not in tarname): # if still no mn
            # try some other fields
            for field in i_csv_filename_mod.split("_"):
                if ("mn" in field) or ("MN" in field):
                    tarname=field
                    tarname_found=True
                    break

    if not tarname_found: # there is no "mn" or "MN" in the csv/dat filename so we will need to look it up in the readme
        tarname = i_csv_filename_mod # we will set the tarname to the full name for the time being
        for key in readme_dict:
            if (tarname in readme_dict[key]):
                if ("mn" in key) or ("MN" in key):
                    tarname = key.split('_')[0]
                    if ("mn" not in tarname) and ("MN" not in tarname):
                        print("ERROR: not found the panel number")
                        exit();
                break

#    print(tarname)
    if (".csv" in tarname):
        tarname=tarname.replace(".csv", "");

    if tarname not in tarfile_dict.keys():
        tarfile_dict[tarname] = []

    if len(tarfile_dict[tarname]) != 0:
        # Check for duplicate csv files
        files_have_same_names=False
        for already_added_csv_filename in tarfile_dict[tarname]:
            if get_filename(already_added_csv_filename) == get_filename(i_csv_filename): # if the file names are identical
                # check if the contents are identical
                files_have_same_names=True
#                print(get_filename(i_csv_filename), get_filename(already_added_csv_filename));
                with open(already_added_csv_filename, "rb") as file_a, open(i_csv_filename, "rb") as file_b:
                    if file_a.read() != file_b.read(): # files have different contents
                        tarfile_dict[tarname].append(i_csv_filename)
#                        print("not identical")
                        break
        if not files_have_same_names:
            tarfile_dict[tarname].append(i_csv_filename)

    else: # put the first csv file in
        tarfile_dict[tarname].append(i_csv_filename)
#    counter=counter+1

# print("\nMap of tarfile to csv files:")
# counter=0
# for name in tarfile_dict:
#     if (counter<5):
#         print(name+" -> "+','.join(tarfile_dict[name]))
#     if counter == 5:
#         print("...")
#     elif counter > (len(tarfile_dict)-5):
#         print(name+" -> "+','.join(tarfile_dict[name]))
#     counter=counter+1

# for name in tarfile_dict:
#     if "70" in name or "205" in name:
#         print(name+" -> "+", ".join(tarfile_dict[name])+"\n")

counter=0
for tarname in tarfile_dict.keys():
    i_csv_filenames = tarfile_dict[tarname]

    # Find the earliest and latest time stamps so we can name the tarball
    first_lines=[]
    last_lines=[]
    first_timestamp_dict={}
    last_timestamp_dict={}
    for i_csv_filename in i_csv_filenames:
#        print(i_csv_filename)
        with open(i_csv_filename) as f:
            i_last_line=deque(f, 1)
            if (len(i_last_line)>0):
                i_last_line=i_last_line[0]
            else:
                first_timestamp_dict[i_csv_filename] = "null"
                last_timestamp_dict[i_csv_filename] = "null"
#                print(i_csv_filename+" is empty")
                i_last_line="null"
#                break;

            last_timestamp_dict[i_csv_filename] = "\'"+i_last_line.split(',')[0]+"\'"
#            last_lines.append(deque(f, 1)[0].split(',')[0]) # get just the timestamp
            try:
                last_lines.append(datetime.strptime(i_last_line.split(',')[0], "%Y-%m-%d %H:%M:%S")) # get just the timestamp
            except ValueError:
                try:
                    last_lines.append(datetime.strptime(i_last_line.split(',')[0], "%Y-%m-%d %H:%M")) # get just the timestamp
                except ValueError:
                    try:
                        last_lines.append(datetime.strptime(i_last_line.split(',')[0], "%Y-%m-%d %H:%M:%S.%f")) # get just the timestamp
                    except ValueError:
                        last_timestamp_dict[i_csv_filename] = "null"; # unparseable timestamp
#                        print("No last line :(");
#    print(last_lines)

        # Now get first timestamp
        with open(i_csv_filename) as f:
            for line in f:
                first_timestamp_dict[i_csv_filename] = "\'" + line.split(',')[0] + "\'"
#                print(i_csv_filename, first_timestamp_dict[i_csv_filename])
                try:
                    first_lines.append(datetime.strptime(line.split(',')[0], "%Y-%m-%d %H:%M:%S")) # get just the timestamp
                except ValueError:
                    try:
                        first_lines.append(datetime.strptime(line.split(',')[0], "%Y-%m-%d %H:%M")) # get just the timestamp
                    except ValueError:
                        try:
                            first_lines.append(datetime.strptime(line.split(',')[0], "%Y-%m-%d %H:%M:%S.%f")) # get just the timestamp
                        except ValueError:
                            first_timestamp_dict[i_csv_filename] = "null"; # very old files don't have timestamp...
                break # only want first line

        # we also have dates in the comment ("daq start" and input and log files)
        if (len(first_lines)==0 and len(last_lines)==0):
            try:
                comment = readme_dict[i_csv_filename.split('/')[-1].replace('.csv', '')]
                found = re.search('\d{2}-\d{2}-\d{4}', comment)
                if found != None:
                    date = datetime.strptime(found.group(), '%m-%d-%Y')
                    first_lines.append(date)
                    last_lines.append(date)
            except KeyError:
                # try .dat instead of .csv
                for key in readme_dict:
                    if i_csv_filename.split('/')[-1] in readme_dict[key]:
                        comment = readme_dict[key]
                        break
                    #            print(comment)
                found = re.search('\d{4}-\d{2}-\d{2}', comment)
                if found != None:
                    date = datetime.strptime(found.group(), '%Y-%m-%d')
                    first_lines.append(date)
                    last_lines.append(date)
                else:
                    print("ERROR: not found a date for "+i_csv_filename)
                    date=""
                #                exit()


    first_date = "YYYYMMDD" # default dates in case there are not timestamps...
    last_date = "YYYYMMDD"
    if (len(first_lines)>0):
        first_date = min(first_lines).strftime("%Y%m%d")
    if (len(last_lines)>0):
        last_date = max(last_lines).strftime("%Y%m%d")
#    print(last_lines)
#    print(first_date, last_date)
#    exit(1)
    tarball_filename = "bck.mu2e.PanelQC_HV.Fe55."+tarname+"_"+first_date+"_"+last_date+".tbz"

    print("Tarring up "+tarball_filename+"...")
    tar = tarfile.open(tarball_filename, "w:gz")

    for i_csv_filename in i_csv_filenames:
        tarred_name = get_filename(i_csv_filename)
        for member in tar.getmembers():
            if "hv-data/"+tarred_name == member.name:
                tarred_name = tarred_name.replace('.csv', '')+"_"+".csv" # just in case there are files with the same name, we want to be able to extract them all later
                break
        print("\t adding "+i_csv_filename+"...")
        tar.add(i_csv_filename, arcname="hv-data/"+tarred_name) # just want the csvfilename not the whole directory structure
        i_csv_filename_mod = i_csv_filename.split('/')[-1].replace('.csv', '').replace('currvstime_', '').replace('currvstime', '').replace('crampdata_','').replace('crampdata','').replace('MN','mn')
        i_csv_filename_mod = re.sub('a[0-9]_', '', i_csv_filename_mod, count=1)
#        print(i_csv_filename_mod)
        try:
#            print("Trying to find "+i_csv_filename_mod)
            comment = readme_dict[i_csv_filename_mod]
#            print(i_csv_filename_mod+" *was* found in README")
        except KeyError:
            print(i_csv_filename_mod+" was not found in README")
            comment = "was not found in README"

#        print(i_csv_filename)
        try:
            input_filename = input_dict[i_csv_filename.split('/')[-1].replace('.csv', '')]
            tarred_input_name = input_filename.split('/')[-1]
#            print(input_filename, tarred_input_name)
            print("\t adding "+input_filename+"...")
            tar.add(input_filename, arcname="hv-data/"+tarred_input_name)
        except KeyError:
            # somtimes the input file names are called input_a1_YYYY-MM-DD-HH-mm.txt but the input_dict is keyed to the entry
            # in the README, which is usually in the input filename
            comment=""
            for key in readme_dict:
                if i_csv_filename.split('/')[-1] in readme_dict[key]:
                    comment = readme_dict[key]
                    break
            actual_input_filename=""
            input_file_found=False
            for input_filename in input_filenames:
                if input_filename.split('/')[-1].split('.')[0] in comment: # .split('.')[0] removes file type because sometimes there is a typo in the README
                    actual_input_filename = input_filename
                    input_file_found=True
                    break
                if (input_file_found):
                    break
            if not input_file_found:
                if "pedestal" not in i_csv_filename:
                    print("\tCouldn't find input file for "+i_csv_filename+". Check if it was specified in README...")
#                exit()
            else:
#                exit()
                print("\t adding "+actual_input_filename+"...")
                tarred_input_name = actual_input_filename.split('/')[-1]
                tar.add(actual_input_filename, arcname="hv-data/"+tarred_input_name)

        try:
            log_filename = log_dict[i_csv_filename.split('/')[-1].replace('.csv', '')]
            tarred_log_name = log_filename.split('/')[-1]
#            print(log_filename, tarred_log_name)
            print("\t adding "+log_filename+"...")
            tar.add(log_filename, arcname="hv-data/"+tarred_log_name)
        except KeyError:
            # somtimes the log file names are called log_a1_YYYY-MM-DD-HH-mm.txt but the log_dict is keyed to the entry
            # in the README, which is usually in the log filename
            comment=""
            for key in readme_dict:
                if i_csv_filename.split('/')[-1] in readme_dict[key]:
                    comment = readme_dict[key]
                    break
            actual_log_filename=""
            log_file_found=False
            for log_filename in log_filenames:
                if log_filename.split('/')[-1].split('.')[0] in comment:
                    actual_log_filename = log_filename
                    log_file_found=True
                    break
                if (log_file_found):
                    break
            if not log_file_found:
                if "pedestal" not in i_csv_filename:
                    print("\tCouldn't find log file for "+i_csv_filename+". Check if it was specified in README...")
            else:
                print("\t adding "+actual_log_filename+"...")
                tarred_log_name = actual_log_filename.split('/')[-1]
                tar.add(actual_log_filename, arcname="hv-data/"+tarred_log_name)


        if (counter > 0):
            insert_sql_file.write(",");
        insert_sql_file.write("\n(" + get_panel_id(tarname) + ", \'" + tarred_name + "\', " + first_timestamp_dict[i_csv_filename] + ", " + last_timestamp_dict[i_csv_filename] + ", \'" + tarball_filename + "\', \'" + comment + "\')")
        counter=counter+1
    tar.close()
#    exit(1)

insert_sql_file.write(";\n\nINSERT INTO qc.panel_hv_data_readmes(filename, last_modified, text) VALUES ");

counter=0
for readme_filename in readme_filenames:
    readme_file = open(readme_filename, 'r')
    text = readme_file.readlines()
    if counter>0:
        insert_sql_file.write(",")
    insert_sql_file.write("\n(\'"+get_filename(readme_filename)+"\', \'" + time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(time.ctime(os.path.getmtime(readme_filename)))) + "\', \'"+add_escape_chars("".join(text))+"\')");
    counter=counter+1

print("Done!");
print("Total Number of Files Archived = "+str(len(input_filenames) + len(csv_filenames) + len(log_filenames)))
print("\t"+str(len(csv_filenames))+" csv/dat files, "+str(len(input_filenames))+" input files, and "+str(len(log_filenames))+" log files")
print("Now check " + outfilename + " looks OK and then run the following command:")
print("  psql -h ifdb11 -p 5459 mu2e_tracker_prd < " + outfilename)
