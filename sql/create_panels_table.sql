set role mu2e_tracker_admin;

create schema qc;
grant usage on schema qc to public;

create table qc.panels (
       	panel_id integer primary key,
	missing_straws integer[] DEFAULT '{}',
	high_current_wires integer[] DEFAULT '{}',
	blocked_straws integer[] DEFAULT '{}',
	sparking_wires integer[] DEFAULT '{}',
	no_hv_straw_hv integer[] DEFAULT '{}',
	no_hv_straw_cal integer[] DEFAULT '{}',
	missing_omega_pieces integer[] DEFAULT '{}',
	loose_omega_pieces integer[] DEFAULT '{}',
	short_wires integer[] DEFAULT '{}',
	max_erf_fit real[] DEFAULT '{}',
	missing_anode integer[] DEFAULT '{}',
	missing_cathode integer[] DEFAULT '{}',
	rise_time real[] DEFAULT '{}',
	missing_wires integer[] DEFAULT '{}',
	maxerf_risetime_filenames text[] DEFAULT '{}',
	earboard BOOLEAN,
	hv_test_done BOOLEAN,
	loose_preamp_amb_connections integer[] DEFAULT '{}',
	low_anode_cathode_resistances integer[] DEFAULT '{}',
	passes_final_amb_dmb_leak_check BOOLEAN,
	earflooding_trimming_done BOOLEAN,
	air_test_for_straw_blockage_done BOOLEAN,
	disconnected_preamps integer[] DEFAULT '{}',
	patched_straws integer[] DEFAULT '{}',
	loose_preamp_anode_connections integer[] DEFAULT '{}',
	passes_first_amb_dmb_leak_check BOOLEAN,
	suspicious_preamp_thresholds integer[] DEFAULT '{}',
	short_omega_pieces integer[] DEFAULT '{}',
	survey_hole_problem_hv BOOLEAN,
	survey_hole_problem_mid BOOLEAN,
	survey_hole_problem_cal BOOLEAN,
	kapton_dots integer[] DEFAULT '{}',
	drac_id varchar
);

grant select on qc.panels to public;
grant insert on qc.panels to mu2e_tracker_admin;
grant insert on qc.panels to mu2e_tracker_writer;
grant update on qc.panels to mu2e_tracker_writer;
