import os
import time

def usage():
    print("Usage: python3 create_imported_fnal_planesdb.py path/to/paneldb YYYY_MM_DD")
    print("where YYYY_MM_DD is the snapshot date")
    exit(1);

def replace_problem_chars(string):
    return string.replace(' ', '_').replace('.', '').replace('\'', '').replace("&", "and").replace("-", '').replace("(", '').replace(")", '');

if (len(os.sys.argv) != 3):
    usage()
elif (os.sys.argv[1] == "-h" or os.sys.argv[1] == "--help"):
    usage()

basedir=os.sys.argv[1]
if (not os.path.exists(basedir)):
    print("Directory \"" + basedir + "\" does not exist. Exiting...");
    exit(1);
snapshot_date = os.sys.argv[2]
if ("_" not in snapshot_date):
    print("Format should be YYYY_MM_DD. Exiting...")
    exit(1)

most_recent=0.
print(basedir)
all_contents=[]
with os.scandir(basedir) as plane_dirs:
    for plane_dir in plane_dirs:
        if ('._' in plane_dir.name):
            continue
#        print(plane_dir.name)
        if (plane_dir.is_dir()):
            with os.scandir(basedir+"/"+plane_dir.name) as panel_dirs:
                for panel_dir in panel_dirs:
                    if ('._' in panel_dir.name):
                        continue
                    if (panel_dir.is_dir()):
                        print(plane_dir.name+"/"+panel_dir.name)
                        if ('094' in panel_dir.name): # this is a duplicate
                            continue
                        with os.scandir(basedir+"/"+plane_dir.name+"/"+panel_dir.name) as panel_files:
                            for panel_file in panel_files:
                                if ('._' in panel_file.name):
                                    continue
                                if (panel_file.is_file()):
                                    this_contents={}
                                    filename=basedir+"/"+plane_dir.name+"/"+panel_dir.name+"/"+panel_file.name;
                                    this_contents["panel_id"] = int(panel_dir.name);
                                    this_contents["file_name"] = replace_problem_chars(panel_file.name);
#                                    print(mtime);
                                    f = open(filename, 'r')
                                    contents = f.read()
                                    this_contents["file_content"] = "\""+contents.replace("'", "")+"\"";
#                                    mtime = time.ctime(os.path.getmtime(filename))
                                    mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(time.ctime(os.path.getmtime(filename))))
                                    this_contents["last_modified"] = mtime;
                                    if (os.path.getmtime(filename) > most_recent):
                                        most_recent = os.path.getmtime(filename)
                                    all_contents.append(this_contents)

print("Most recent = ", time.ctime(most_recent))
create_sql_file = open('../sql/create_imported_fnal_planesdb.sql', 'w')
create_sql_file.write("set role mu2e_tracker_admin;\n")
#create_sql_file.write("create schema imported;\n")
#create_sql_file.write("grant usage on schema imported to public;\n")
create_sql_file.write("DROP TABLE imported.fnal_planes_previous;\n"); # drop the current table, we will recreate it at the end
create_sql_file.write("CREATE TABLE imported.fnal_planes_previous AS SELECT * FROM imported.fnal_planes;\n")
create_sql_file.write("GRANT SELECT ON imported.fnal_planes_previous TO public;\n");
create_sql_file.write("DROP TABLE imported.fnal_planes;\n"); # drop the current table, we will recreate it at the end
table_name = "imported.fnal_planes_"+snapshot_date
create_sql_file.write("CREATE TABLE "+table_name+"(id integer primary key, panel_id integer, file_name text, file_contents text, last_modified timestamp);\n")

create_sql_file.write("grant select on "+table_name+" to public;\n");
create_sql_file.write("grant insert on "+table_name+" to mu2e_tracker_admin;\n");

counter=0
insert_sql_file = open('../sql/insert_imported_fnal_planesdb.sql', 'w')
insert_sql_file.write('INSERT INTO '+table_name+'(id, panel_id, file_name, file_contents, last_modified)\n')
insert_sql_file.write("VALUES");
for content in all_contents:
    if (counter > 0):
        insert_sql_file.write(",");
    insert_sql_file.write("\n(")
    insert_sql_file.write(str(counter)+",");
    for column in content:
        if column == "panel_id":
            insert_sql_file.write(" "+str(content[column]));
        elif column == "last_modified":
            insert_sql_file.write(", '"+str(content[column])+"'");
        else:
            insert_sql_file.write(", '"+str(content[column]+"'"));
    insert_sql_file.write(")");
    counter=counter+1;
#    if counter > 2:
#        break
insert_sql_file.write(";\n");
insert_sql_file.write("CREATE TABLE imported.fnal_planes AS SELECT * FROM "+table_name+";\n")
insert_sql_file.write("GRANT SELECT ON imported.fnal_planes TO public;")
