set role mu2e_tracker_admin;

drop schema measurements CASCADE;
create schema measurements;
grant usage on schema measurements to public;

create table measurements.plane_heights (
       height_measurement_id SERIAL primary key,
	plane_id integer,
	phi_location_deg float,
	height_inches float,
	date_taken date
);

grant select on measurements.plane_heights to public;
grant insert on measurements.plane_heights to mu2e_tracker_admin;

create table measurements.plane_pins (
       pin_measurement_id SERIAL primary key,
	plane_id integer,
	top_panel_id integer,
	bottom_panel_id integer,
	pin_position integer,
	pin_inches float,
	date_taken date
);

grant select on measurements.plane_pins to public;
grant insert on measurements.plane_pins to mu2e_tracker_admin;

create table measurements.plane_gaps (
       gap_measurement_id SERIAL primary key,
	plane_id integer,
	panel_id integer,
	gap_ccw_mm float,
	date_taken date
);

grant select on measurements.plane_gaps to public;
grant insert on measurements.plane_gaps to mu2e_tracker_admin;

create table measurements.panel_leaks (
       leak_measurement_id SERIAL primary key,
	panel_id integer,
	leak_sccm float,
	comment text,
	date_taken date
);


grant select on measurements.panel_leaks to public;
grant insert on measurements.panel_leaks to mu2e_tracker_admin;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA measurements TO mu2e_tracker_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA measurements TO mu2e_tracker_writer;
