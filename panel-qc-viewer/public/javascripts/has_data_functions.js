
export function has_hv_data(panel_info) {

    if (panel_info['high_current_wires'].length != 0 ||
	panel_info['sparking_wires'].length != 0 ||
	panel_info['short_wires'].length != 0 ||
	panel_info['max_erf_fit'].length != 0) {

	return true;
    }
    else {
	return false;
    }
}
