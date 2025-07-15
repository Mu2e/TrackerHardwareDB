
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


    var img_traveler = document.getElementById('img_traveler');
    img_traveler.src =  "images/travelers/MN" + panel_number.toString().padStart(3,'0') + "_Traveler.pdf";
});
