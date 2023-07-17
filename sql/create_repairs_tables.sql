set role mu2e_tracker_admin;

drop schema repairs CASCADE;
create schema repairs;
grant usage on schema repairs to public;

create table repairs.panels (
       	repair_id SERIAL primary key,
	panel_id integer,
	column_changed text,
	old_value text,
	new_value text,
	date_uploaded date,
	comment text
);

create table repairs.planes (
       	repair_id SERIAL primary key,
	plane_id integer,
	column_changed text,
	old_value text,
	new_value text,
	date_uploaded date,
	comment text
);

grant select on repairs.panels to public;
grant insert on repairs.panels to mu2e_tracker_admin;
grant insert on repairs.panels to mu2e_tracker_writer;
grant update on repairs.panels to mu2e_tracker_writer;

grant select on repairs.planes to public;
grant insert on repairs.planes to mu2e_tracker_admin;
grant insert on repairs.planes to mu2e_tracker_writer;
grant update on repairs.planes to mu2e_tracker_writer;
