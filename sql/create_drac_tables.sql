set role mu2e_tracker_admin;

drop schema drac CASCADE;
create schema drac;
grant usage on schema drac to public;

create table drac.roc_configs (
       roc_config_id SERIAL primary key,
        device_serial varchar, 
	design_info varchar, 
	design_ver varchar, 
	back_level_ver varchar,
	UNIQUE(device_serial, design_info, design_ver, back_level_ver)
);
grant select on drac.roc_configs to public;
grant insert on drac.roc_configs to mu2e_tracker_admin;

create table drac.cal_configs (
       cal_config_id SERIAL primary key,
        id_read varchar, 
	silsig varchar, 
	design_name varchar, 
	checksum varchar,
	design_info varchar,
	design_ver varchar,
	back_level varchar,
	debug_info varchar,
	dsn varchar,
	UNIQUE(id_read, silsig, design_name, checksum, design_info, design_ver, back_level, debug_info, dsn)
);
grant select on drac.cal_configs to public;
grant insert on drac.cal_configs to mu2e_tracker_admin;

create table drac.test_results (
       drac_test_id SERIAL primary key,
       drac_id varchar,
       panel_id int,
       roc_config_id int,
       cal_config_id int
);
grant select on drac.test_results to public;
grant insert on drac.test_results to mu2e_tracker_admin;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA drac TO mu2e_tracker_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA drac TO mu2e_tracker_writer;
