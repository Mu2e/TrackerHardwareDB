set role mu2e_tracker_admin;

CREATE TABLE qc.panel_hv_data_files(
       file_id SERIAL primary key,
       panel_id integer,
       filename text unique,
       first_timestamp timestamp,
       last_timestamp timestamp,
       tarball text,
       comment text
);

CREATE TABLE qc.panel_hv_data_readmes(
       file_id SERIAL primary key,
       filename text,
       last_modified timestamp,
       text text
);


grant select on qc.panel_hv_data_files to public;
grant insert on qc.panel_hv_data_files to mu2e_tracker_admin;
grant select on qc.panel_hv_data_readmes to public;
grant insert on qc.panel_hv_data_readmes to mu2e_tracker_admin;
