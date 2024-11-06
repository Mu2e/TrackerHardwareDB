export function get_panels_in_plane(plane_info) {

    var panel_positions=['pos0', 'pos1', 'pos2', 'pos3', 'pos4', 'pos5']
    var panels = Array();
    for (let i_panel = 0; i_panel < panel_positions.length; ++i_panel) {
	if (plane_info['panel_ids'].length>0) { // some planes have not been updated to the new 6-column format
	    if (i_panel < plane_info['panel_ids'].length) { // some planes don't have all their panels yet
		panels.push(plane_info['panel_ids'][i_panel]);
	    }
	}
	else {
	    let panel_pos = panel_positions[i_panel]
	    if (plane_info['panel_id_'+panel_pos] != null) {
		panels.push(plane_info['panel_id_'+panel_pos]);
	    }
	}
    }
    return panels;
}

// true = 6-column format, false = 1-column format
export function get_panels_col_format(plane_info) {

    if (plane_info['panel_ids'].length>0) { // some planes have not been updated to the new 6-column format
	return false;
    }
    else if (get_panels_in_plane(plane_info).length == 0) {
	return false; // no panels in plane at all
    }
    else {
	return true;
    }
}
