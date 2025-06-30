export function single_channel_issues() {
    return ["missing_straws", "missing_wires", "high_current_wires", "blocked_straws", "short_wires", "sparking_wires", "missing_anode", "missing_cathode", "missing_omega_pieces", "no_hv_straw_cal", "no_hv_straw_hv", "loose_preamp_amb_connections", "low_anode_cathode_resistances", "disconnected_preamps", "patched_straws", "loose_preamp_anode_connections", "suspicious_preamp_thresholds", "short_omega_pieces", "kapton_dots", "bad_calibration_pulses", "bad_jumper_dmb_connection"];
}

export function dead_channel_issues() {
    return ["missing_straws", "missing_wires", "short_wires", "missing_anode", "missing_cathode", "missing_omega_pieces", "no_hv_straw_cal", "no_hv_straw_hv", "disconnected_preamps", "short_omega_pieces"];
}
