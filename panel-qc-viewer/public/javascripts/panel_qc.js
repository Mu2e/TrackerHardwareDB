
import { plot_panel_qc } from './panel_qc_plot.js'
import { draw_repairs_table } from './repairs_table.js'

const form = document.querySelector("form");
const log = document.querySelector("#log");

const showPanelButton = document.getElementById('btnShowPanel');
showPanelButton.addEventListener('click', async function () {
    var output = "";
    var panel_number = parseInt(document.getElementById('panel_number').value);    
    if (!isNaN(panel_number)) {
	const response = await fetch('getPanel/'+panel_number);
	const panel_info = await response.json();

	// Output the full return to the verbose output section
	document.getElementById("log").innerHTML = JSON.stringify(panel_info,
								  undefined,
								  2);

	output = "Panel "+panel_number;
	if (panel_info.length==0) {
	    output += " not found!";
	}
	else {
	    straw_status_plot = document.getElementById('straw_status_plot');
	    let summary_table = document.getElementById('summary');
	    var returned_output = plot_panel_qc(panel_info, straw_status_plot, summary_table);
	    output += returned_output;

	}
    }
    else {
	output = "Input must be a number";
    }

    document.getElementById("panel_info").innerHTML = output;

    // Now make the measurement plots
    let panel_leak_budget = 0.014;
    let measurement_output = "Leak Measurements (panel leak budget: " + panel_leak_budget + " sccm)\n";
    measurement_output += "=================================================\n"
    const leak_response = await fetch('getMeasurements/panel/leaks/'+panel_number);
    const leak_measurements = await leak_response.json();
    if (leak_measurements.length != 0) {
	for (let i_leak_measurement = 0; i_leak_measurement < leak_measurements.length; ++i_leak_measurement) {
	    let leak_sccm = leak_measurements[i_leak_measurement]["leak_sccm"];
	    let frac_of_budget = (leak_sccm / panel_leak_budget)*100;
	    measurement_output += leak_measurements[i_leak_measurement]['date_taken'] + " (" + leak_measurements[i_leak_measurement]['comment'] + ") = " +  leak_sccm.toFixed(4) + " sccm (" + frac_of_budget.toFixed(1) + "% of panel leak budget)\n";
	}
    }
    else {
	measurement_output += "\nLeak Measurements: none found\n";
    }
    document.getElementById("measurement_info").innerHTML = measurement_output;
    
    // Now do the repairs table
    if (!isNaN(panel_number)) {
	const repairs_table_response = await fetch('getPanelRepairs/'+panel_number);
	const repairs_table_info = await repairs_table_response.json();

	var over_table = document.getElementById("panel_repairs_table");
	draw_repairs_table(repairs_table_info, over_table);
    }
    else {
	output = "Input must be a number";
    }


    // Add traveler image
    var img_traveler = document.getElementById('img_traveler');
    img_traveler.src =  "images/travelers/MN" + panel_number.toString().padStart(3,'0') + "_Traveler.pdf";

    // Add FNAL Planes DB section
    let fnal_plane_db_options = document.getElementById("fnal_plane_db_file_select");
    const fnal_plane_db_response = await fetch('getPanelFromFNALPlanesDB/'+panel_number);
    const fnal_plane_db_panel_info = await fnal_plane_db_response.json();
    if (fnal_plane_db_panel_info.length>0) {
	for (let i_row = 0; i_row < fnal_plane_db_panel_info.length; ++i_row) {
	    var this_panel_fnal_plane_db = fnal_plane_db_panel_info[i_row]
	    // If there is no content in the file, ignore it
	    if (this_panel_fnal_plane_db["file_contents"] == "\"\"") {
		continue;
	    }
	    var file_name = this_panel_fnal_plane_db["file_name"];
	    const newOption = document.createElement('option');
	    newOption.textContent = file_name;
	    newOption.value = file_name;
	    fnal_plane_db_options.appendChild(newOption);
	}
    }

    fnal_plane_db_options.addEventListener('change', (event) => {
	let file_contents_div = document.getElementById('fnal_plane_db_file_contents');
	var file_contents = "error retrieving file contents";
	for (let i_row = 0; i_row < fnal_plane_db_panel_info.length; ++i_row) {
	    var this_panel_fnal_plane_db = fnal_plane_db_panel_info[i_row]
	    var file_name = this_panel_fnal_plane_db["file_name"];
	    if (file_name == fnal_plane_db_options.value) {
		file_contents = this_panel_fnal_plane_db["file_contents"];
		break;
	    }
	}
	file_contents_div.textContent = file_contents;
    })


});
