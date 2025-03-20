set role mu2e_tracker_admin;

create table qc.planes (
	plane_id integer primary key,
	panel_id_pos0 integer NULL,
	panel_id_pos1 integer NULL,
	panel_id_pos2 integer NULL,
	panel_id_pos3 integer NULL,
	panel_id_pos4 integer NULL,
	panel_id_pos5 integer NULL,
	construction_start_date date,
	construction_end_date date
);

grant select on qc.planes to public;
grant insert on qc.planes to mu2e_tracker_admin;
grant insert on qc.planes to mu2e_tracker_writer;
grant update on qc.planes to mu2e_tracker_writer;
