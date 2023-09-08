
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
	    var returned_output = plot_panel_qc(panel_info, straw_status_plot);
	    output += returned_output;

	}
    }
    else {
	output = "Input must be a number";
    }
	    
    document.getElementById("panel_info").innerHTML = output;

    // Now do the table

    if (!isNaN(panel_number)) {
	const repairs_table_response = await fetch('getPanelRepairs/'+panel_number);
	const repairs_table_info = await repairs_table_response.json();

	var over_table = document.getElementById("panel_repairs_table");
	draw_repairs_table(repairs_table_info, over_table);
    }
    else {
	output = "Input must be a number";
    }
});
