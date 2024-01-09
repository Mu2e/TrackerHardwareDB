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

create table drac.hv_configs (
       hv_config_id SERIAL primary key,
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
grant select on drac.hv_configs to public;
grant insert on drac.hv_configs to mu2e_tracker_admin;

create table drac.test_results (
       drac_test_id SERIAL primary key,
       drac_id varchar,
       panel_id int,
       roc_config_id int,
       cal_config_id int,
       hv_config_id int,
       I3_3 real,
       I2_5 real,
       I1_8HV real,
       IHV5_0 real,
       VDMBHV5_0 real,
       V1_8HV real,
       V3_3HV real,
       V2_5 real,
       A0 real,
       A1 real,
       A2 real,
       A3 real,
       I1_8CAL real,
       I1_2 real,
       ICAL5_0 real,
       ADCSPARE real,
       V3_3 real,
       VCAL5_0 real,
       V1_8CAL real,
       V1_0 real,
       ROCPCBTEMP real,
       HVPCBTEMP real,
       CALPCBTEMP real,
       RTD real,
       ROC_RAIL_1V_mV real,
       ROC_RAIL_1_8V_mV real,
       ROC_RAIL_2_5V_mV real,
       ROC_TEMP_degC real,
       CAL_RAIL_1V_mV real,
       CAL_RAIL_1_8V_mV real,
       CAL_RAIL_2_5V_mV real,
       CAL_TEMP_degC real,
       HV_RAIL_1V_mV real,
       HV_RAIL_1_8V_mV real,
       HV_RAIL_2_5V_mV real,
       HV_TEMP_degC real,
       TEMP_degC real,
       VOLT_2_5V real,
       VOLT_5_1V real,
       pulser_total_hv integer[],
       pulser_total_cal integer[],
       pulser_total_coinc integer[],
       pulser_total_time_counts integer[],
       pulser_rate_hv_Hz real[],
       pulser_rate_cal_Hz real[],
       pulser_rate_coinc_Hz real[],
       delta_t_rms real[]
);
grant select on drac.test_results to public;
grant insert on drac.test_results to mu2e_tracker_admin;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA drac TO mu2e_tracker_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA drac TO mu2e_tracker_writer;
