
export function has_hv_data(panel_info) {

    // if (panel_info['high_current_wires'].length != 0 ||
    // 	panel_info['sparking_wires'].length != 0 ||
    // 	panel_info['short_wires'].length != 0 ||
    // 	panel_info['max_erf_fit'].length != 0) {
    if (panel_info['hv_test_done']) {
	return true;
    }
    else {
	return false;
    }
}


export function has_fe55_data(panel_info) {

    if (panel_info['max_erf_fit'].length != 0) {

	return true;
    }
    else {
	return false;
    }
}
